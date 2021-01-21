
@Library('dst-shared@master') _

dockerBuildPipeline {
    repository = "cray"
    imagePrefix = ""
    app = "cfs-trust"
    name = "cfs-trust"
    description = "Configuration Framework Service Trust Environment"
    product = "csm"
    enableSonar = true
    autoJira = false

    githubPushRepo = "Cray-HPE/cfs-trust"
    /*
        By default all branches are pushed to GitHub

        Optionally, to limit which branches are pushed, add a githubPushBranches regex variable
        Examples:
        githubPushBranches =  /master/ # Only push the master branch
        
        In this case, we push bugfix, feature, hot fix, master, and release branches
    */
    githubPushBranches =  /(bugfix\/.*|feature\/.*|hotfix\/.*|master|release\/.*)/ 
}
