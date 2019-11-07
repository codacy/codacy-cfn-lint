#!/usr/bin/env python3

import os
import sys
import glob
import json
import importlib.util

# cfn-lint's source code is very well organized. Every rule is a class, and every class is systematically
# documented, for instance:
#
# (...)
#   class Aliases(CloudFormationLintRule):
#       """Check if CloudFront Aliases are valid domain names"""
#       id = 'E3013'
#       shortdesc = 'CloudFront Aliases'
#       description = 'CloudFront aliases should contain valid domain names'
#       source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-distributionconfig.html#cfn-cloudfront-distribution-distributionconfig-aliases'
#       tags = ['properties', 'cloudfront']
# (...)
#
# Thus, in order to get the docs we can just find all source files, instantiate the class, and get its documentation.
# That is what this script, does do create patterns.json, description.json, and the markdown description for each rule.
# It further creates the ./docs folder and places everything in its right place.


def get_class_instance(path, path_prefix, class_name=""):
    """Get and instantiate class contained in a given souce file

    :param path        : source file containing a class we wish to instantiate
    :param path_prefix : prefix which sould be removed from the path to get the module name
    :return            : an instance of the class
    """
    module_name = path.replace(path_prefix, "").replace(
        ".py", "").replace("/", ".")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not class_name:
        return getattr(module, module_name.split(".")[-1])
    else:
        return getattr(module, class_name)


def get_patterns(rule_class_instance):
    """Extract patterns from a rule class instance

    :param rule_class_instance : rule class instance from where to extract patterns
    :return                    : dictionary with Codacy patterns info
    """
    level_map = dict(W="Warning", E="Error", I="Info")
    category_map = dict(W="CodeStyle", E="ErrorProne", I="Documentation")
    return dict(patternId=rule_class_instance.id,
                level=level_map[rule_class_instance.id[0]],
                category=category_map[rule_class_instance.id[0]])


def get_docs(rule_class_instance):
    """Extract documents from a rule class instance

    :param rule_class_instance : rule class instance from where to extract documents
    :return                    : dictionary with Codacy documents info
    """
    return dict(patternId=rule_class_instance.id,
                title=rule_class_instance.shortdesc,
                description=rule_class_instance.__doc__,
                timeToFix=5)


def write_description(desc_path, rule_class_instance):
    """Write rule description file

    :param desc_path           : path where to place description files
    :param rule_class_instance : rule class instance from where to extract info
    """
    desc_file = open("%s/%s.md" % (desc_path, rule_class_instance.id), 'w')
    desc_file.write("%s\n\n[SOURCE](%s)" % (
        rule_class_instance.description, rule_class_instance.source_url))


def get_cfnlint_version(version_file):
    """Get cfn-lint version

    :param  version_file : file from where to extract version
    :return              : version number
    """
    vline = list(filter(lambda x: "__version__" in x,
                        open(version_file, "r").readlines()))[0]
    return vline.split("=")[1].strip().replace("'", "")


if len(sys.argv) != 2:
    print("usage: %s <cfn-lint source base dir>" % sys.argv[0])
    sys.exit(1)
else:
    cfnlint_path = sys.argv[1]


os.makedirs("./docs/description", mode=0o755)


desc_file = open('./docs/tool-description.md', 'w')
desc_file.write(
    "CloudFormation Linter is a tool to validate CloudFormation yaml/json")
desc_file.write(
    "templates against the CloudFormation spec and additional checks.")
desc_file.write(
    " Includes checking valid values for resource properties and best practices.")
desc_file.write(" [Learn more](https://github.com/awslabs/cfn-python-lint)")

docs = list()
pats = dict(name="CloudFormation Linter", version=get_cfnlint_version(
    "%s/src/cfnlint/version.py" % cfnlint_path), patterns=list())

# Parse general rules
for path in glob.iglob("%s/src/cfnlint/rules/**/*.py" % cfnlint_path, recursive=True):

    if path.split('/')[-1] == "__init__.py":
        continue
    print(path)
    rule_class = get_class_instance(path, "%s/src/" % cfnlint_path)
    if(rule_class.id):
        pats['patterns'].append(get_patterns(rule_class))
        docs.append(get_docs(rule_class))
        write_description("./docs/description", rule_class)

# Special case for yaml general errors
parse_error_class = get_class_instance(
    "%s/src/cfnlint/__init__.py" % cfnlint_path, "%s/src/" % cfnlint_path, "ParseError")
pats['patterns'].append(get_patterns(parse_error_class))
docs.append(get_docs(parse_error_class))
write_description("./docs/description", parse_error_class)

transform_error_class = get_class_instance(
    "%s/src/cfnlint/__init__.py" % cfnlint_path, "%s/src/" % cfnlint_path, "TransformError")
pats['patterns'].append(get_patterns(transform_error_class))
docs.append(get_docs(transform_error_class))
write_description("./docs/description", transform_error_class)

rule_error_class = get_class_instance(
    "%s/src/cfnlint/__init__.py" % cfnlint_path, "%s/src/" % cfnlint_path, "RuleError")
pats['patterns'].append(get_patterns(rule_error_class))
docs.append(get_docs(rule_error_class))
write_description("./docs/description", rule_error_class)

pats_file = open('./docs/patterns.json', 'w')
pats_file.write(json.dumps(pats, indent=4, sort_keys=True))

docs_file = open('./docs/description/description.json', 'w')
docs_file.write(json.dumps(docs, indent=4, sort_keys=True))
