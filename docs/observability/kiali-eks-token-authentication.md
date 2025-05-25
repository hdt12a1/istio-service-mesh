# Getting Service Account Tokens for Kiali Authentication in EKS

This guide explains how to create a service account and obtain its token for authenticating with Kiali in an Amazon EKS cluster.

## Method 1: Using kubectl to Get an Existing Token

If Kiali is already installed, it creates a service account. You can get its token:

```bash
# Get the name of the Kiali service account
KIALI_SA=$(kubectl get serviceaccount -n istio-system -l app=kiali -o jsonpath='{.items[0].metadata.name}')

# For Kubernetes v1.24+
# Create a token for the service account
kubectl create token $KIALI_SA -n istio-system
```

The command will output a JWT token that you can copy and paste into the Kiali login screen.

## Method 2: Creating a Dedicated Service Account for Kiali Access

If you want to create a dedicated service account for accessing Kiali:

### Step 1: Create a Service Account

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kiali-viewer
  namespace: istio-system
EOF
```

### Step 2: Create a ClusterRole with Appropriate Permissions

```bash
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kiali-viewer
rules:
- apiGroups: [""]
  resources:
  - configmaps
  - endpoints
  - namespaces
  - nodes
  - pods
  - services
  - replicationcontrollers
  verbs:
  - get
  - list
  - watch
- apiGroups: ["extensions", "apps"]
  resources:
  - deployments
  - replicasets
  - statefulsets
  - daemonsets
  verbs:
  - get
  - list
  - watch
- apiGroups: ["batch"]
  resources:
  - jobs
  - cronjobs
  verbs:
  - get
  - list
  - watch
- apiGroups: ["networking.k8s.io"]
  resources:
  - ingresses
  verbs:
  - get
  - list
  - watch
- apiGroups: ["networking.istio.io", "security.istio.io", "extensions.istio.io", "telemetry.istio.io"]
  resources: ["*"]
  verbs:
  - get
  - list
  - watch
EOF
```

### Step 3: Bind the ClusterRole to the Service Account

```bash
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kiali-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kiali-viewer
subjects:
- kind: ServiceAccount
  name: kiali-viewer
  namespace: istio-system
EOF
```

### Step 4: Create a Token for the Service Account

For Kubernetes v1.24+:

```bash
# Create a token with 24-hour expiration
kubectl create token kiali-viewer -n istio-system --duration=24h
```

For longer-lived tokens in Kubernetes v1.24+, create a secret:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: kiali-viewer-token
  namespace: istio-system
  annotations:
    kubernetes.io/service-account.name: kiali-viewer
type: kubernetes.io/service-account-token
EOF

# Get the token
kubectl get secret kiali-viewer-token -n istio-system -o jsonpath='{.data.token}' | base64 --decode
```

## Method 3: Using AWS IAM for EKS Authentication (Advanced)

For production environments, you might want to use AWS IAM for authentication:

### Step 1: Create an IAM Role with Appropriate Permissions

Use the AWS Management Console or AWS CLI to create an IAM role with the necessary permissions to access your EKS cluster.

### Step 2: Map the IAM Role to a Kubernetes RBAC Role

```bash
# Edit the aws-auth ConfigMap
kubectl edit configmap aws-auth -n kube-system
```

Add the following under the `mapRoles` section:

```yaml
mapRoles:
  - rolearn: arn:aws:iam::<AWS_ACCOUNT_ID>:role/<IAM_ROLE_NAME>
    username: kiali-viewer
    groups:
      - kiali-viewers
```

### Step 3: Create a Group and RoleBinding

```bash
# Create a ClusterRoleBinding for the group
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kiali-viewers
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kiali-viewer
subjects:
- kind: Group
  name: kiali-viewers
  apiGroup: rbac.authorization.k8s.io
EOF
```

### Step 4: Get AWS Credentials

Use the AWS CLI to assume the role and get credentials:

```bash
aws sts assume-role --role-arn arn:aws:iam::<AWS_ACCOUNT_ID>:role/<IAM_ROLE_NAME> --role-session-name KialiSession
```

## Using the Token with Kiali

Once you have obtained the token:

1. Access the Kiali UI (through port-forwarding or Ingress)
2. When prompted for authentication, select "Token" authentication
3. Paste the token you obtained into the token field
4. Click "Log In"

## Troubleshooting

### Token Rejected

If your token is rejected:

1. Check that the service account has the necessary permissions
2. Verify that the token hasn't expired
3. Check Kiali logs for more details:
   ```bash
   kubectl logs -n istio-system -l app=kiali
   ```

### Permission Issues

If you can log in but can't see resources:

1. Check that the service account has permissions for all namespaces you want to view
2. Verify that the ClusterRole includes all necessary resource types
3. Check if namespace isolation is enabled in Istio

## Best Practices

1. **Use short-lived tokens**: For security, prefer tokens with a limited lifetime
2. **Least privilege**: Give the service account only the permissions it needs
3. **Dedicated accounts**: Create separate service accounts for different users or teams
4. **Audit access**: Regularly review who has access to Kiali
5. **Consider OpenID Connect**: For production environments, consider setting up OpenID Connect authentication
