import yaml
from pathlib import Path
import hashlib
import subprocess

class YamlTemplate:
    """
    helper class to build yaml file from template.
    yaml template can be provided as string or load from file
    """

    def __init__(self, template):
        self.__template = template

    def build(self, destination, **kwargs):
        with open(destination, 'w') as output:
            parsed = yaml.safe_load(self.__template.format(**kwargs))
            yaml.dump(parsed, output)

    def build2(self, destination, **kwargs):
        with open(destination, 'w') as output:
            print(self.__template.format(**kwargs), file=output)

    @staticmethod
    def load(source):
        with open(source, 'r') as input:
            template = input.read().strip()
        return YamlTemplate(template)

def create_password_hash(email, password):
    h = hashlib.sha256()
    h.update(str.encode(f'{email}{password}', 'utf-8'))
    return h.hexdigest()

CB_PATH = Path(".")
MANIFESTS_DIR = CB_PATH / "etc"/"output"

INSTANCE_ID_CONFIG_MAP_TEMPLATE = CB_PATH / "etc" / "instance-id.yaml"
INSTANCE_ID_CONFIG_MAP_PATH = MANIFESTS_DIR / "instance-id-config-map.yaml"

CLUSTER_TYPE_CONFIG_MAP_TEMPLATE = CB_PATH / "etc" / "cluster-type.yaml"
CLUSTER_TYPE_CONFIG_MAP_PATH = MANIFESTS_DIR / "cluster-type-config-map.yaml"

INFRA_SUBSCRIPTION_PATH = MANIFESTS_DIR / "infra-subscription.yaml"
HUB_SUBSCRIPTION_PATH = MANIFESTS_DIR / "hub-subscription.yaml"
CAPIG_SUBSCRIPTION_PATH = MANIFESTS_DIR / "capig-subscription.yaml"
PL_SUBSCRIPTION_PATH = MANIFESTS_DIR / "pl-subscription.yaml"

INFRA_INSTANCE_TEMPLATE = CB_PATH / "etc" / "infra-instance.yaml"
INFRA_INSTANCE_PATH = MANIFESTS_DIR / "infra-instance.yaml"

def set_project_id():
    process = subprocess.Popen(['gcloud', 'projects', 'list'],
                        universal_newlines=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # print(stdout, stderr)
    projects_candidates = stdout.split('\n\n')

    i=1
    for project in projects_candidates:
        print('\n-------- Project ', i, '--------\n')
        print(project.strip())
        print('\n----------------------------\n')
        i=i+1
    project_num = input('Please select your GCP project for installation (Enter a number): \n')
    ##TODO validate input
    # print (stdout.split('\n\n'))
    project_id = 'undefined'
    project_info_list = projects_candidates[int(project_num)-1].split('\n')
    for project_info in project_info_list:
        if project_info.startswith('PROJECT_ID'):
            project_id = project_info.split(': ')[1]

    print('You selected Project ID is:', project_id)
    process = subprocess.Popen(['gcloud', 'config', 'set','project', project_id],
                        universal_newlines=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout, stderr)

def generate_k8s_manifests(domain_name, admin_email, admin_password):
    YamlTemplate.load(INFRA_INSTANCE_TEMPLATE).build(
        INFRA_INSTANCE_PATH,
        access_token='"' + "access_token" + '"',
        admin_email=admin_email,
        admin_password='"' + admin_password + '"',
        api_version="v12.0",
        app_secret='zLld3AoRwf8rkPxggv5u',
        aws_region="aws_region",
        business_id="business_id",
        index_tag="1.5.0",
        multitenant_enabled="true",
        pl_enabled="false",
        mariadb_enabled="mariadb_enabled",
        cors_allowed_domains=[],
        domain_name=domain_name,
        password_hash=create_password_hash(admin_email, admin_password),
        pixel_id="pixel_id",
        registry="public.ecr.aws/fbconvservice",
        telemetry_consent="true",
        s3_bucket="s3_bucket",
        main_stack_name="main_stack_name",
        enable_certificate_arn="",
        ssl_redirect="ssl_redirect",
        http_protocol="http_protocol",
        # operators installation status
        hub_op_installed="true",
        capig_op_installed="true",
        pl_op_installed="false"
    )

if __name__ == '__main__':
    print('\n\nWelcome to Conversions API Gateway installation wizard!\n')
    print('Here are list of your existing GCP projects in your account: \n')

    set_project_id()
    domain_name = input('Enter your domain name for Conversions API Gateway: \n')
    admin_email = input('Enter your account email for Conversions API Gateway: \n')
    admin_password = input('Enter your password for Conversions API Gateway: \n')
    # domain_name = "gke.chaoyih.cbinternal.com"
    # admin_email = "chaoyih@fb.com"
    # admin_password = "1234"
    generate_k8s_manifests(domain_name, admin_email, admin_password)
    print('Creating Kubernetes mannifests....')

    print('Installing Conversions API Gateway....')
