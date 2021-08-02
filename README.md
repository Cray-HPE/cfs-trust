CFS Needs to be able to communicate in an authenticated trusted way with various environments;
this requires a trust relation in the form of SSH keys and signed certificates from vault.

This code base aims to implement setup actions that have been outlined in the PKI trust document
for CMS services:
https://connect.us.cray.com/confluence/display/CASMPET/Public+Key+Infrastructure+%28PKI%29+Services#PublicKeyInfrastructure(PKI)Services-ManagementPlaneBootstrappingandContinuousOperation

In the first approach deliverable, existing key setup information that was inherited from BIS nodes
will be replaced with generated credential information that is stored in kubernetes secrets. AEEs
then reference this information each time they need to authenticate into hosts that have been bootstrapped.

## Versioning
We use [SemVer](http://semver.org/). The version is generated at build time by the
version.py script in the [cms-meta-tools ](https://github.com/Cray-HPE/cms-meta-tools) repo,
and then written to the .version file.

All other files either read from that file or have the version string written to them at
build time based on the information in the [update_versions.conf](update_versions.conf) file. 

Since the migration to github, there is also some additional version massaging that takes place
in [Jenkinsfile.github](Jenkinsfile.github).

In order to make it easier to go from a version number back to the source code that produced that version,
some information about the most recent git commit is added at build time to build artifacts.
For RPMs, it is added to the changelog. For Helm charts, it is added as annotations metadata. And for
Docker images, it is written to gitInfo.txt in the root of the container. This is done using the
git_info tool in cms-meta-tools, which is called automatically by the runBuildPrep script.

## Build Helpers
This repo uses some build helper scripts from the cms-meta-tools repo. See that repo for more details.

## Copyright and License
This project is copyrighted by Hewlett Packard Enterprise Development LP and is under the MIT
license. See the [LICENSE](LICENSE) file for details.

When making any modifications to a file that has a Cray/HPE copyright header, that header
must be updated to include the current year.

When creating any new files in this repo, if they contain source code, they must have
the HPE copyright and license text in their header, unless the file is covered under
someone else's copyright/license (in which case that should be in the header). For this
purpose, source code files include Dockerfiles, Ansible files, RPM spec files, and shell
scripts. It does **not** include Jenkinsfiles, OpenAPI/Swagger specs, or READMEs.

When in doubt, provided the file is not covered under someone else's copyright or license, then
it does not hurt to add ours to the header.
