param(
    [string]$WorkspaceRoot = "D:\Forge"
)

$ErrorActionPreference = "Continue"

$ForgeRepoName = "le-the-forge"
$DataRepoName = "last-epoch-data"
$ForgeRepo = Join-Path $WorkspaceRoot $ForgeRepoName
$DataRepo = Join-Path $WorkspaceRoot $DataRepoName
$SkipDirectories = @(
    ".git",
    "node_modules",
    ".venv",
    "venv",
    ".venv311",
    ".venv313",
    ".python311",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "coverage",
    ".cache",
    ".mypy_cache",
    ".ruff_cache",
    ".vite",
    ".next",
    # Local extraction/output folders are intentionally skipped to keep this health check bounded.
    "exports_json",
    "extracted_raw",
    "game_files",
    "il2cpp_dump",
    "patch_versions",
    "reports"
)
$SearchExtensions = @(
    ".ps1",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".example",
    ".txt"
)
$OldPathNeedles = @("D:\LastEpochTools", "D:\Programming\the-forge")
$Results = [ordered]@{}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "== $Title =="
}

function Set-Check {
    param(
        [string]$Name,
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Status,
        [string]$Message
    )

    $Results[$Name] = [pscustomobject]@{
        Status = $Status
        Message = $Message
    }
}

function Add-Check {
    param(
        [string]$Name,
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Status,
        [string]$Message
    )

    if (-not $Results.Contains($Name)) {
        Set-Check -Name $Name -Status $Status -Message $Message
        return
    }

    $Current = $Results[$Name]
    $Rank = @{ PASS = 0; WARN = 1; FAIL = 2 }
    $FinalStatus = $Current.Status
    if ($Rank[$Status] -gt $Rank[$Current.Status]) {
        $FinalStatus = $Status
    }

    $FinalMessage = $Current.Message
    if ($Message) {
        if ($FinalMessage) {
            $FinalMessage = "$FinalMessage; $Message"
        } else {
            $FinalMessage = $Message
        }
    }

    Set-Check -Name $Name -Status $FinalStatus -Message $FinalMessage
}

function Test-CommandAvailable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-External {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    $OriginalLocation = Get-Location
    try {
        if ($WorkingDirectory) {
            Set-Location -LiteralPath $WorkingDirectory
        }

        $Output = & $FilePath @Arguments 2>&1
        $ExitCode = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }

        return [pscustomobject]@{
            ExitCode = $ExitCode
            Output = @($Output | ForEach-Object { $_.ToString() })
        }
    } catch {
        return [pscustomobject]@{
            ExitCode = 1
            Output = @($_.Exception.Message)
        }
    } finally {
        Set-Location -LiteralPath $OriginalLocation
    }
}

function Write-SafeCommandOutput {
    param(
        [string[]]$Output,
        [int]$First = 40
    )

    $SensitivePattern = "SECRET|PASSWORD|TOKEN|WEBHOOK|API[_-]?KEY|CLIENT_SECRET"
    $Output |
        Select-Object -First $First |
        ForEach-Object {
            if ($_ -match $SensitivePattern) {
                Write-Host "  [redacted sensitive-looking line]"
            } else {
                Write-Host "  $_"
            }
        }

    if ($Output.Count -gt $First) {
        Write-Host "  ... output truncated ..."
    }
}

function Get-JsonFile {
    param([string]$Path)
    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        Write-Host "Could not parse JSON: $Path"
        Write-Host "  $($_.Exception.Message)"
        return $null
    }
}

function Test-PathPartSkipped {
    param([string]$RelativePath)
    $Parts = $RelativePath -split "[/\\]"
    foreach ($Part in $Parts) {
        if ($SkipDirectories -contains $Part) {
            return $true
        }
    }
    return $false
}

function Get-SearchExtension {
    param([System.IO.FileInfo]$File)

    if ($File.Name -eq ".env") {
        return ".env"
    }

    if ($File.Name.EndsWith(".example", [System.StringComparison]::OrdinalIgnoreCase)) {
        return ".example"
    }

    return $File.Extension.ToLowerInvariant()
}

function Get-SearchFiles {
    param([string]$RepoPath)

    $Files = New-Object System.Collections.Generic.List[string]
    $SkippedDirs = 0
    $SkippedFiles = 0
    $Stack = New-Object System.Collections.Generic.Stack[string]
    $Stack.Push($RepoPath)

    while ($Stack.Count -gt 0) {
        $CurrentDir = $Stack.Pop()

        try {
            $Entries = @(Get-ChildItem -LiteralPath $CurrentDir -Force -ErrorAction Stop)
        } catch {
            $SkippedDirs++
            continue
        }

        foreach ($Entry in $Entries) {
            if ($Entry.PSIsContainer) {
                if ($SkipDirectories -contains $Entry.Name) {
                    $SkippedDirs++
                    continue
                }

                $Stack.Push($Entry.FullName)
                continue
            }

            $Extension = Get-SearchExtension -File $Entry
            if ($SearchExtensions -contains $Extension) {
                $Files.Add($Entry.FullName)
            }
        }
    }

    return [pscustomobject]@{
        Files = @($Files)
        SkippedDirs = $SkippedDirs
        SkippedFiles = $SkippedFiles
    }
}

function Get-PythonExecutable {
    param([string]$VenvPath)

    $Candidates = @(
        Join-Path $VenvPath "Scripts\python.exe"
        Join-Path $VenvPath "bin\python"
        Join-Path $VenvPath "bin\python.exe"
    )

    foreach ($Candidate in $Candidates) {
        if (Test-Path -LiteralPath $Candidate) {
            return $Candidate
        }
    }

    return $null
}

function Test-GitRepo {
    param(
        [string]$RepoPath,
        [string]$RepoLabel,
        [string]$ExpectedRemoteFragment,
        [string]$CheckName
    )

    Write-Section "$RepoLabel git"

    if (-not (Test-Path -LiteralPath $RepoPath)) {
        Write-Host "Missing repo folder: $RepoPath"
        Add-Check -Name $CheckName -Status "FAIL" -Message "missing repo folder"
        return
    }

    if (-not (Test-Path -LiteralPath (Join-Path $RepoPath ".git"))) {
        Write-Host "Missing .git directory: $RepoPath"
        Add-Check -Name $CheckName -Status "FAIL" -Message "missing .git directory"
        return
    }

    if (-not (Test-CommandAvailable "git")) {
        Write-Host "git is not available on PATH."
        Add-Check -Name $CheckName -Status "WARN" -Message "git unavailable"
        return
    }

    $Status = Invoke-External -FilePath "git" -Arguments @("status", "--short") -WorkingDirectory $RepoPath
    Write-Host "git status --short:"
    if ($Status.Output.Count -gt 0) {
        $Status.Output | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Host "  clean"
    }

    $Remotes = Invoke-External -FilePath "git" -Arguments @("remote", "-v") -WorkingDirectory $RepoPath
    Write-Host "git remote -v:"
    if ($Remotes.Output.Count -gt 0) {
        $Remotes.Output | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Host "  no remotes configured"
    }

    if ($Status.ExitCode -ne 0 -or $Remotes.ExitCode -ne 0) {
        $CombinedGitOutput = (($Status.Output + $Remotes.Output) -join "`n")
        if ($CombinedGitOutput -match "dubious ownership") {
            Write-Host "FAIL: Git refused this repository because of safe.directory ownership protection."
            Write-Host "Suggested command:"
            Write-Host "  git config --global --add safe.directory $($RepoPath -replace '\\','/')"
            Add-Check -Name $CheckName -Status "FAIL" -Message "git safe.directory ownership check blocked verification"
        } else {
            Write-Host "FAIL: git status or git remote failed."
            Add-Check -Name $CheckName -Status "FAIL" -Message "git command failed"
        }
        return
    }

    if (($Remotes.Output -join "`n") -notmatch [regex]::Escape($ExpectedRemoteFragment)) {
        Add-Check -Name $CheckName -Status "FAIL" -Message "remote does not contain $ExpectedRemoteFragment"
        Write-Host "FAIL: expected a remote containing $ExpectedRemoteFragment"
    } else {
        Add-Check -Name $CheckName -Status "PASS" -Message "remote matches"
    }

    $Uncommitted = @($Status.Output | Where-Object { $_ -and ($_ -notmatch "^warning:") })
    if ($Uncommitted.Count -gt 0) {
        Add-Check -Name $CheckName -Status "WARN" -Message "$($Uncommitted.Count) uncommitted status line(s)"
        Write-Host "Uncommitted changes: yes"
    } else {
        Write-Host "Uncommitted changes: no"
    }
}

function Test-WorkspaceLayout {
    Write-Section "Workspace layout"

    $Failures = @()
    foreach ($Path in @($WorkspaceRoot, $ForgeRepo, $DataRepo)) {
        if (Test-Path -LiteralPath $Path) {
            Write-Host "PASS: found $Path"
        } else {
            Write-Host "FAIL: missing $Path"
            $Failures += $Path
        }
    }

    foreach ($Path in @($ForgeRepo, $DataRepo)) {
        $GitPath = Join-Path $Path ".git"
        if (Test-Path -LiteralPath $GitPath) {
            Write-Host "PASS: found $GitPath"
        } else {
            Write-Host "FAIL: missing $GitPath"
            $Failures += $GitPath
        }
    }

    if ($Failures.Count -gt 0) {
        Set-Check -Name "workspace layout" -Status "FAIL" -Message "missing critical path(s)"
    } else {
        Set-Check -Name "workspace layout" -Status "PASS" -Message "expected folders and .git directories found"
    }
}

function Test-OldHardcodedPaths {
    Write-Section "Old hardcoded path scan"

    $Matches = @()
    $SkippedFileCount = 0
    $RepoScanCounts = [ordered]@{}
    $ReposToScan = @(
        [pscustomobject]@{ Label = "le-the-forge"; Path = $ForgeRepo },
        [pscustomobject]@{ Label = "last-epoch-data"; Path = $DataRepo }
    )

    foreach ($Repo in $ReposToScan) {
        $RepoPath = $Repo.Path
        if (-not (Test-Path -LiteralPath $RepoPath)) {
            continue
        }

        Write-Host "Scanning old paths in $($Repo.Label)..."
        $SearchPlan = Get-SearchFiles -RepoPath $RepoPath
        $RepoScanCounts[$Repo.Label] = $SearchPlan.Files.Count
        Write-Host "  Candidate files: $($SearchPlan.Files.Count)"
        if ($SearchPlan.SkippedDirs -gt 0) {
            Write-Host "  Skipped directories: $($SearchPlan.SkippedDirs)"
        }

        foreach ($File in $SearchPlan.Files) {
            try {
                $Found = Select-String -LiteralPath $File -SimpleMatch -Pattern $OldPathNeedles -ErrorAction Stop
                if ($Found) {
                    $Matches += $Found
                }
            } catch {
                $SkippedFileCount++
            }
        }
    }

    foreach ($Entry in $RepoScanCounts.GetEnumerator()) {
        Write-Host "Scanned $($Entry.Value) files in $($Entry.Key)."
    }
    if ($SkippedFileCount -gt 0) {
        Write-Host "Skipped $SkippedFileCount unreadable file(s)."
    }

    if ($Matches.Count -eq 0) {
        Write-Host "PASS: no old hardcoded paths found."
        $Message = "no old paths found"
        if ($SkippedFileCount -gt 0) {
            $Message = "$Message; $SkippedFileCount unreadable file(s) skipped"
        }
        Set-Check -Name "old hardcoded path scan" -Status "PASS" -Message $Message
        return
    }

    Write-Host "WARN: found old hardcoded path references. Review and update manually if still active:"
    $Matches |
        Sort-Object Path, LineNumber |
        ForEach-Object {
            $Relative = $_.Path
            Write-Host ("  {0}:{1}: {2}" -f $Relative, $_.LineNumber, $_.Line.Trim())
        }

    $Message = "$($Matches.Count) old path reference(s)"
    if ($SkippedFileCount -gt 0) {
        $Message = "$Message; $SkippedFileCount unreadable file(s) skipped"
    }
    Set-Check -Name "old hardcoded path scan" -Status "WARN" -Message $Message
}

function Test-Frontend {
    Write-Section "le-the-forge frontend"

    $PackageJsonPath = Join-Path $ForgeRepo "frontend\package.json"
    $NodeModulesPath = Join-Path $ForgeRepo "frontend\node_modules"
    $TsConfigPath = Join-Path $ForgeRepo "frontend\tsconfig.json"
    $HasWarnings = $false

    if (Test-CommandAvailable "node") {
        $NodeVersion = Invoke-External -FilePath "node" -Arguments @("--version") -WorkingDirectory $ForgeRepo
        Write-Host "node: $($NodeVersion.Output -join ' ')"
    } else {
        Write-Host "WARN: node is not available on PATH."
        $HasWarnings = $true
    }

    if (Test-CommandAvailable "npm") {
        $NpmVersion = Invoke-External -FilePath "npm" -Arguments @("--version") -WorkingDirectory $ForgeRepo
        Write-Host "npm: $($NpmVersion.Output -join ' ')"
    } else {
        Write-Host "WARN: npm is not available on PATH."
        $HasWarnings = $true
    }

    if (-not (Test-Path -LiteralPath $PackageJsonPath)) {
        Write-Host "WARN: missing frontend/package.json"
        Set-Check -Name "frontend toolchain" -Status "WARN" -Message "missing frontend/package.json"
        return
    }

    $PackageJson = Get-JsonFile -Path $PackageJsonPath
    if ($PackageJson -and $PackageJson.scripts) {
        Write-Host "Detected frontend scripts:"
        $PackageJson.scripts.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)"
        }
    }

    if (-not (Test-Path -LiteralPath $NodeModulesPath)) {
        Write-Host "WARN: frontend dependencies are missing."
        Write-Host "Suggested command: cd $ForgeRepo\frontend; npm install"
        Set-Check -Name "frontend toolchain" -Status "WARN" -Message "frontend dependencies missing"
        return
    }

    if (-not (Test-CommandAvailable "npm")) {
        Set-Check -Name "frontend toolchain" -Status "WARN" -Message "npm unavailable"
        return
    }

    $HasTypecheckScript = $false
    if ($PackageJson -and $PackageJson.scripts) {
        $HasTypecheckScript = [bool]($PackageJson.scripts.PSObject.Properties.Name -contains "typecheck")
    }

    if ($HasTypecheckScript) {
        Write-Host "Running: npm run typecheck"
        $TypeCheck = Invoke-External -FilePath "npm" -Arguments @("run", "typecheck") -WorkingDirectory (Join-Path $ForgeRepo "frontend")
    } elseif (Test-Path -LiteralPath $TsConfigPath) {
        Write-Host "Running: npx --no-install tsc --noEmit"
        $TypeCheck = Invoke-External -FilePath "npx" -Arguments @("--no-install", "tsc", "--noEmit") -WorkingDirectory (Join-Path $ForgeRepo "frontend")
    } else {
        Write-Host "WARN: no typecheck script or frontend/tsconfig.json found."
        Set-Check -Name "frontend toolchain" -Status "WARN" -Message "no TypeScript check available"
        return
    }

    if ($TypeCheck.Output.Count -gt 0) {
        $TypeCheck.Output | ForEach-Object { Write-Host "  $_" }
    }

    if ($TypeCheck.ExitCode -eq 0) {
        $Status = if ($HasWarnings) { "WARN" } else { "PASS" }
        Set-Check -Name "frontend toolchain" -Status $Status -Message "TypeScript check completed"
    } else {
        Set-Check -Name "frontend toolchain" -Status "WARN" -Message "TypeScript check returned exit code $($TypeCheck.ExitCode)"
    }
}

function Test-Backend {
    Write-Section "le-the-forge backend"

    $RequirementsPath = Join-Path $ForgeRepo "backend\requirements.txt"
    $VenvPath = Join-Path $ForgeRepo "backend\.venv"
    $BackendPath = Join-Path $ForgeRepo "backend"
    $HasWarnings = $false

    if (Test-CommandAvailable "python") {
        $PythonVersion = Invoke-External -FilePath "python" -Arguments @("--version") -WorkingDirectory $ForgeRepo
        Write-Host "python: $($PythonVersion.Output -join ' ')"
    } else {
        Write-Host "WARN: python is not available on PATH."
        $HasWarnings = $true
    }

    if (Test-Path -LiteralPath $RequirementsPath) {
        Write-Host "PASS: backend/requirements.txt exists."
    } else {
        Write-Host "WARN: backend/requirements.txt is missing."
        $HasWarnings = $true
    }

    if (-not (Test-Path -LiteralPath $VenvPath)) {
        Write-Host "WARN: backend/.venv is missing."
        Write-Host "Suggested commands:"
        Write-Host "  cd $ForgeRepo\backend"
        Write-Host "  python -m venv .venv"
        Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
        Set-Check -Name "backend toolchain" -Status "WARN" -Message "backend venv missing"
        return
    }

    $VenvPython = Get-PythonExecutable -VenvPath $VenvPath
    if (-not $VenvPython) {
        Write-Host "WARN: backend/.venv exists but no Python executable was found."
        Write-Host "Suggested commands:"
        Write-Host "  cd $ForgeRepo\backend"
        Write-Host "  Remove-Item -Recurse -Force .venv  # only if you intentionally want to recreate it"
        Write-Host "  python -m venv .venv"
        Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
        Set-Check -Name "backend toolchain" -Status "WARN" -Message "backend venv appears broken"
        return
    }

    $VenvVersion = Invoke-External -FilePath $VenvPython -Arguments @("--version") -WorkingDirectory $BackendPath
    Write-Host "backend venv python: $($VenvVersion.Output -join ' ')"

    $PytestVersion = Invoke-External -FilePath $VenvPython -Arguments @("-m", "pytest", "--version") -WorkingDirectory $BackendPath
    if ($PytestVersion.ExitCode -ne 0) {
        Write-Host "WARN: pytest is not available in backend/.venv."
        Write-Host "Suggested command: cd $ForgeRepo\backend; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
        Set-Check -Name "backend toolchain" -Status "WARN" -Message "pytest unavailable in backend venv"
        return
    }

    Write-Host "pytest: $($PytestVersion.Output -join ' ')"
    Write-Host "Running: backend/.venv python -m pytest --collect-only -q -p no:cacheprovider"

    $OldPyDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE
    $env:PYTHONDONTWRITEBYTECODE = "1"
    try {
        $Collect = Invoke-External -FilePath $VenvPython -Arguments @("-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider") -WorkingDirectory $BackendPath
    } finally {
        $env:PYTHONDONTWRITEBYTECODE = $OldPyDontWriteBytecode
    }

    if ($Collect.ExitCode -eq 0) {
        if ($Collect.Output.Count -gt 0) {
            $Collect.Output | Select-Object -First 80 | ForEach-Object { Write-Host "  $_" }
            if ($Collect.Output.Count -gt 80) {
                Write-Host "  ... output truncated ..."
            }
        }
        $Status = if ($HasWarnings) { "WARN" } else { "PASS" }
        Set-Check -Name "backend toolchain" -Status $Status -Message "pytest collection completed"
    } else {
        if ($Collect.Output.Count -gt 0) {
            Write-Host "pytest collection output:"
            Write-SafeCommandOutput -Output ($Collect.Output | Select-Object -Last 80) -First 80
        }
        Set-Check -Name "backend toolchain" -Status "WARN" -Message "pytest collection returned exit code $($Collect.ExitCode)"
    }
}

function Test-DockerCompose {
    Write-Section "le-the-forge docker"

    $ComposeFile = Join-Path $ForgeRepo "docker-compose.yml"
    if (-not (Test-Path -LiteralPath $ComposeFile)) {
        Write-Host "WARN: docker-compose.yml is missing."
        Set-Check -Name "docker compose config" -Status "WARN" -Message "docker-compose.yml missing"
        return
    }

    if (-not (Test-CommandAvailable "docker")) {
        Write-Host "WARN: docker is not available on PATH."
        Set-Check -Name "docker compose config" -Status "WARN" -Message "docker unavailable"
        return
    }

    Write-Host "Running: docker compose config"
    $Compose = Invoke-External -FilePath "docker" -Arguments @("compose", "config") -WorkingDirectory $ForgeRepo

    if ($Compose.ExitCode -eq 0) {
        Write-Host "PASS: docker compose config succeeded. Full rendered config is intentionally not printed."
        Set-Check -Name "docker compose config" -Status "PASS" -Message "compose config succeeded"
    } else {
        Write-Host "WARN: docker compose config failed. Output:"
        Write-SafeCommandOutput -Output $Compose.Output -First 40
        Set-Check -Name "docker compose config" -Status "WARN" -Message "compose config returned exit code $($Compose.ExitCode)"
    }
}

function Test-DataRepoBasics {
    Write-Section "last-epoch-data basics"

    $HasWarnings = $false
    if (Test-CommandAvailable "python") {
        $PythonVersion = Invoke-External -FilePath "python" -Arguments @("--version") -WorkingDirectory $DataRepo
        Write-Host "python: $($PythonVersion.Output -join ' ')"
    } else {
        Write-Host "WARN: python is not available on PATH."
        $HasWarnings = $true
    }

    $CommonFiles = @("README.md", "EXTRACTION_PIPELINE_PLAN.md", "FORGE_DATA_CONTRACT.md", "DATA_BUNDLE_SPEC.md")
    foreach ($File in $CommonFiles) {
        $Path = Join-Path $DataRepo $File
        if (Test-Path -LiteralPath $Path) {
            Write-Host "PASS: found $File"
        } else {
            Write-Host "WARN: missing $File"
            $HasWarnings = $true
        }
    }

    $RequirementsPath = Join-Path $DataRepo "requirements.txt"
    if (Test-Path -LiteralPath $RequirementsPath) {
        Write-Host "PASS: found requirements.txt"
    } else {
        Write-Host "WARN: missing requirements.txt"
        $HasWarnings = $true
    }

    $VenvCandidates = @(".venv", "venv", ".venv311", ".venv313") | ForEach-Object { Join-Path $DataRepo $_ }
    $ExistingVenvs = @($VenvCandidates | Where-Object { Test-Path -LiteralPath $_ })
    if ($ExistingVenvs.Count -eq 0) {
        Write-Host "WARN: no common last-epoch-data venv folder found."
        Write-Host "Suggested commands:"
        Write-Host "  cd $DataRepo"
        Write-Host "  python -m venv .venv"
        Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
        $HasWarnings = $true
    } else {
        foreach ($Venv in $ExistingVenvs) {
            $VenvPython = Get-PythonExecutable -VenvPath $Venv
            if ($VenvPython) {
                $Version = Invoke-External -FilePath $VenvPython -Arguments @("--version") -WorkingDirectory $DataRepo
                if ($Version.ExitCode -eq 0) {
                    Write-Host "venv python: $VenvPython -> $($Version.Output -join ' ')"
                } else {
                    Write-Host "WARN: venv python appears broken: $VenvPython -> $($Version.Output -join ' ')"
                    Write-Host "Suggested commands:"
                    Write-Host "  cd $DataRepo"
                    Write-Host "  python -m venv .venv"
                    Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
                    $HasWarnings = $true
                }
            } else {
                Write-Host "WARN: venv appears broken: $Venv"
                $HasWarnings = $true
            }
        }
    }

    if ($HasWarnings) {
        Set-Check -Name "last-epoch-data basics" -Status "WARN" -Message "basic setup warnings found"
    } else {
        Set-Check -Name "last-epoch-data basics" -Status "PASS" -Message "basic files and venv found"
    }
}

Test-WorkspaceLayout
Test-GitRepo -RepoPath $ForgeRepo -RepoLabel $ForgeRepoName -ExpectedRemoteFragment "NickolisK24/le-the-forge" -CheckName "le-the-forge git"
Test-GitRepo -RepoPath $DataRepo -RepoLabel $DataRepoName -ExpectedRemoteFragment "NickolisK24/last-epoch-data" -CheckName "last-epoch-data git"
Test-OldHardcodedPaths
Test-Frontend
Test-Backend
Test-DockerCompose
Test-DataRepoBasics

Write-Section "Summary"
$Results.GetEnumerator() | ForEach-Object {
    "{0,-28} {1,-5} {2}" -f $_.Key, $_.Value.Status, $_.Value.Message
}

$CriticalFailures = @(
    "workspace layout",
    "le-the-forge git",
    "last-epoch-data git"
) | Where-Object {
    $Results.Contains($_) -and $Results[$_].Status -eq "FAIL"
}

if ($CriticalFailures.Count -gt 0) {
    Write-Host ""
    Write-Host "Critical failure(s): $($CriticalFailures -join ', ')"
    exit 1
}

exit 0
