18 Feb 2025
Based on Pure Storage Support Article
https://support.purestorage.com/bundle/m_pure1_manage_rest_api/page/Pure1/Pure1_Manage/013_Pure1_Manage_-_REST_API/topics/task/t_generate_a_privatepublic_rsa_key_pair.html


Association of the Python client with Pure1 requires two steps:

1.)  Generate a Private/Public RSA Key Pair

generate private key:	openssl genrsa -aes256 -out pure1-py-private.pem 2048
generate public key:	openssl rsa -in pure1-test-private.pem -outform PEM -pubout -out pure1-py-public.pem
copy public key text:	cat pure1-py-public.pem



2.)  Register the Python "Application" in Pure1

authenticate to Pure1
from IAM https://iam.purestorage.com/ select "API Keys" on the left column
press "Register API Key" button on page and give the application a name and paste the public key
from the list of registered APIs copy the "Application ID" for use in the scripts

