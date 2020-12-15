CFS Needs to be able to communicate in an authenticated trusted way with various environments;
this requires a trust relation in the form of SSH keys and signed certificates from vault.

This code base aims to implement setup actions that have been outlined in the PKI trust document
for CMS services:
https://connect.us.cray.com/confluence/display/CASMPET/Public+Key+Infrastructure+%28PKI%29+Services#PublicKeyInfrastructure(PKI)Services-ManagementPlaneBootstrappingandContinuousOperation

In the first approach deliverable, existing key setup information that was inherited from BIS nodes
will be replaced with generated credential information that is stored in kubernetes secrets. AEEs
then reference this information each time they need to authenticate into hosts that have been bootstrapped.
