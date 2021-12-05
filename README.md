# AWS-based API
AWS-based API, serverless, Dynamo DB, Pydantic

#How to install serverless framework:
* make sure NPM is installed on your system
* npm init
* accept defalut settings, press "Enter"
* npm config set prefix /usr/local (macOS/Ubuntu "fix" for path)
* in case of some permission issues - sudo chown -R $USER /usr/local/lib
* npm install -g serverless
* serverless -version (to check whether it is installed correctly)
* npm install --save serverless-python-requirements

#Configure AWS CLI, detailed instructions can be found here:
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html
#...and here:
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

#Configure severless handler via "serverless.yml"

#Once you have functions ready and everything configured start your API instance with:
* serverless deploy -v



