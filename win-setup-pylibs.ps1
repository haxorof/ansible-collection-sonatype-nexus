$CollectionPath = "$PSScriptRoot\.pylibs\ansible_collections\haxorof\sonatype_nexus"
$ParentCollectionPath = Split-Path $CollectionPath -Parent
if (-not (Test-Path $ParentCollectionPath)) {
    New-Item -ItemType Directory -Path "$PSScriptRoot\.pylibs\ansible_collections\haxorof" -Force
}
$ExecCmd = "New-Item -ItemType SymbolicLink -Path '$CollectionPath' -Target '$PSScriptRoot'"
if (-not (Test-Path $CollectionPath)) {
    Write-Host "Creating symbolic link $CollectionPath"
    Start-Process powershell -Verb RunAs -ArgumentList $ExecCmd
} else {
    Write-Host "Symbolic link $CollectionPath already exists!"
}