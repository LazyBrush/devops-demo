# devops-demo

These are some notes from 'lets play with kubernetes'

# Bootstrap - environment

It can be problematic running terraform, different versions and on different OSes. E.g. creating certs in terraform uses openssl library, and can be different on OSX to Linux, or that's my experience, for consistency lets use VSCode's devcontainer and always run in linux (container) for issuing terraform and aws commands.

    See .devcontainer directory, copied from k8s one I made a while ago, updated to add terraform

If we were making this usable from multiple users, we would store the terraform state in an S3 bucket.

# K8s

Lets get an EKS to play with. We could do a simple docker compose or minikube, but we want a 'real' K8s to play with.

AWS and Terraform, have their taster ones. Let's get it.

    From https://learn.hashicorp.com/tutorials/terraform/eks
    Repo https://github.com/hashicorp/learn-terraform-provision-eks-cluster

Change some values are we counting pennies. Actually, t3 medium and small, that's fine for an hour or two of play.

Kick it all off with:

    cd eks; terraform init; terraform apply

Note: Did have to change the versions.tf to allow using a newer version of terraform. Will see if there are any issues...

Note: Also at this point, in the AWS console to see things being created. Will want to check later when we kill everything that all resources are removed. We do trust terraform, mostly.

Note: Hmm, cluster made in Ohio, nice. Will update REGION later, preference is for London. (variables.tf)

# Get context

    aws eks update-kubeconfig --name education-eks-xxxxx --region=us-east-2

Note: next time, I'll set my preferred region and cluster name will vary. After setting context can then:

    kubectl get pods

# EKS deploy failure

After 30 mins, we get an error, timing out on EKS node group creation...

Got the error:

    Error: error waiting for EKS Node Group (education-eks-xxx:node-group-2-xxx) to create: unexpected state 'CREATE_FAILED', wanted target 'ACTIVE'. last error: 1 error occurred:

    eks-node-group-2-xxx-xxx-xxx: AsgInstanceLaunchFailures: You've reached your quota for maximum Fleet Requests for this account. Launching EC2 instance failed.

Going to https://us-east-2.console.aws.amazon.com/servicequotas/home/services can see that ASG had limits on targets (perhaps a red herring)

Also, seems others having this issue as recently as 11 days ago asking for update: https://github.com/terraform-aws-modules/terraform-aws-eks/issues/2149

# Attempt #2

Try:

- In my home region where I may have increased limits over time
- Single node group, single node

Same error. Seems the defaults for fleet should allow creation, yet it fails. Submitted request for fleet increase in eu-west-2. Perhaps my account is old and new defaults have not been applied?

Lets move on with _any_ k8s system.

# Minikube

Run up a minikube, first install it, https://minikube.sigs.k8s.io/docs/start/ then:

    minikube start --embed-certs

Note: we start with certs in the .kube/config such that they are accessible from the vscode container.

Note: However, minikube has 127.0.0.1 in .kube/config file which is not the container 127.0.0.1 and trying the host.docker.internal breaks the cert connection.

OK, giving up on a vscode dev container for running tools.

# Checkpoint

At this point we have a cluster to do things with, although not on AWS this should be mostly representative and good enough for testing most things, minus fancy ELBs and Route53 type stuff.

We use Lens to view into the cluster.

# Nginx

Taken from https://github.com/nginxinc/docker-nginx/tree/master/stable/alpine and put in containe-nginx dir

Manually tested with:

    docker build -t demo-nginx .
    docker run -p 80:80 -it demo-nginx

And then browse to http://localhost:80

# Little more interesting

Simple flask app in container-app which outputs an env var, if set

# Deploy and Config folder

Simple 3 replica deployment for flask app, with the env var set to being the pod name. Nginx pointing at the demo-app service, so we see a different pod name if we refresh in the browser.

# Checkpoint

Using port forwarding, we can open browser and see it do something useful. 'deploy' and 'config' folders added manually with:

- kubectl apply -k . (in config folder)
- kubectl apply -f nginx-deploy.yaml (in deploy folder)
- kubectl apply -f app-service.yaml
- kubectl apply -f app-deploy.yaml

# Pipelines! Build and Deploy

Lets try running concourse in the cluster. See https://github.com/concourse/concourse-chart

    helm repo add concourse https://concourse-charts.storage.googleapis.com/
    helm install my-release concourse/concourse

Laptop whirring, not starting up.
