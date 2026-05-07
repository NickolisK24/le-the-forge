param(
    [string]$WorkspaceRoot = "D:\Forge"
)

$ErrorActionPreference = "Continue"

$LeRepo = Join-Path $WorkspaceRoot "le-the-forge"
$DataRepo = Join-Path $WorkspaceRoot "last-epoch-data"
$BundleDir = Join-Path $DataRepo "data_bundle"
$BackendDir = Join-Path $LeRepo "backend"
$DataGenerator = Join-Path $DataRepo "tools\scripts\generate_data_bundle_skeleton.py"
$DataValidator = Join-Path $DataRepo "tools\scripts\validate_data_bundle.py"
$ForgeCompatScript = Join-Path $BackendDir "scripts\check_data_bundle.py"
$BackendPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

$Results = [ordered]@{}
$CriticalFailure = $false

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "== $Title =="
}

function Set-Result {
    param(
        [string]$Name,
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Status,
        [string]$Message
    )
    $script:Results[$Name] = [pscustomobject]@{
        Status = $Status
        Message = $Message
    }
    if ($Status -eq "FAIL") {
        $script:CriticalFailure = $true
    }
}

function Join-ProcessArguments {
    param([string[]]$Arguments)

    $quoted = foreach ($Argument in $Arguments) {
        if ($null -eq $Argument) {
            '""'
        } elseif ($Argument -match '[\s"]') {
            '"' + ($Argument -replace '"', '\"') + '"'
        } else {
            $Argument
        }
    }

    return ($quoted -join " ")
}

function Invoke-CapturedProcess {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $FilePath
    $psi.Arguments = Join-ProcessArguments -Arguments $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi

    try {
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        return [pscustomobject]@{
            ExitCode = $process.ExitCode
            Stdout = $stdout
            Stderr = $stderr
        }
    } catch {
        return [pscustomobject]@{
            ExitCode = 1
            Stdout = ""
            Stderr = $_.Exception.Message
        }
    } finally {
        $process.Dispose()
    }
}

function Write-ProcessOutput {
    param(
        [string]$Stdout,
        [string]$Stderr
    )

    if ($Stdout) {
        Write-Host "stdout:"
        $Stdout.TrimEnd() -split "`r?`n" | ForEach-Object { Write-Host "  $_" }
    }
    if ($Stderr) {
        Write-Host "stderr:"
        $Stderr.TrimEnd() -split "`r?`n" | ForEach-Object { Write-Host "  $_" }
    }
}

function Require-Path {
    param(
        [string]$Label,
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        Write-Host "PASS: $Label -> $Path"
        return $true
    }

    Write-Host "FAIL: missing $Label -> $Path"
    return $false
}

Write-Section "Phase 1D read-only handoff smoke test"
Write-Host "Workspace root: $WorkspaceRoot"
Write-Host "This smoke test does not replace production loaders."
Write-Host "This smoke test does not start the app."
Write-Host "This smoke test does not load family JSON files into production registries."
Write-Host "This smoke test only verifies the control-plane handoff."

Write-Section "Preflight"
$preflightOk = $true
$preflightOk = (Require-Path "workspace root" $WorkspaceRoot) -and $preflightOk
$preflightOk = (Require-Path "le-the-forge repo" $LeRepo) -and $preflightOk
$preflightOk = (Require-Path "last-epoch-data repo" $DataRepo) -and $preflightOk
$preflightOk = (Require-Path "le-the-forge .git" (Join-Path $LeRepo ".git")) -and $preflightOk
$preflightOk = (Require-Path "last-epoch-data .git" (Join-Path $DataRepo ".git")) -and $preflightOk
$preflightOk = (Require-Path "last-epoch-data generator" $DataGenerator) -and $preflightOk
$preflightOk = (Require-Path "last-epoch-data validator" $DataValidator) -and $preflightOk
$preflightOk = (Require-Path "Forge compatibility script" $ForgeCompatScript) -and $preflightOk
$preflightOk = (Require-Path "Forge backend venv Python" $BackendPython) -and $preflightOk

if (-not $preflightOk) {
    Set-Result "preflight" "FAIL" "required workspace path or script is missing"
    Write-Section "Summary"
    $Results.GetEnumerator() | ForEach-Object {
        "{0,-38} {1,-5} {2}" -f $_.Key, $_.Value.Status, $_.Value.Message
    }
    Write-Host "Overall result: FAIL"
    exit 1
}
Set-Result "preflight" "PASS" "required paths found"

Write-Section "last-epoch-data generation"
$generation = Invoke-CapturedProcess -FilePath "python" -Arguments @("tools\scripts\generate_data_bundle_skeleton.py") -WorkingDirectory $DataRepo
Write-ProcessOutput -Stdout $generation.Stdout -Stderr $generation.Stderr
if ($generation.ExitCode -ne 0) {
    Set-Result "last-epoch-data generation" "FAIL" "exit code $($generation.ExitCode)"
} else {
    Set-Result "last-epoch-data generation" "PASS" "bundle skeleton generated"
}

if ($CriticalFailure) {
    Write-Section "Summary"
    $Results.GetEnumerator() | ForEach-Object {
        "{0,-38} {1,-5} {2}" -f $_.Key, $_.Value.Status, $_.Value.Message
    }
    Write-Host "Overall result: FAIL"
    exit 1
}

Write-Section "last-epoch-data validation"
$validation = Invoke-CapturedProcess -FilePath "python" -Arguments @("tools\scripts\validate_data_bundle.py") -WorkingDirectory $DataRepo
Write-ProcessOutput -Stdout $validation.Stdout -Stderr $validation.Stderr
if ($validation.ExitCode -ne 0) {
    Set-Result "last-epoch-data validation" "FAIL" "exit code $($validation.ExitCode)"
} elseif ($validation.Stdout -match "Status:\s+WARN|Result:\s+WARN") {
    Set-Result "last-epoch-data validation" "WARN" "validator passed with expected Phase 1 warnings"
} else {
    Set-Result "last-epoch-data validation" "PASS" "validator passed"
}

if ($CriticalFailure) {
    Write-Section "Summary"
    $Results.GetEnumerator() | ForEach-Object {
        "{0,-38} {1,-5} {2}" -f $_.Key, $_.Value.Status, $_.Value.Message
    }
    Write-Host "Overall result: FAIL"
    exit 1
}

Write-Section "le-the-forge compatibility reader"
$compat = Invoke-CapturedProcess -FilePath $BackendPython -Arguments @("scripts\check_data_bundle.py", "--bundle-dir", $BundleDir, "--json") -WorkingDirectory $BackendDir
if ($compat.Stderr) {
    Write-Host "stderr:"
    $compat.Stderr.TrimEnd() -split "`r?`n" | ForEach-Object { Write-Host "  $_" }
}

if ($compat.ExitCode -ne 0) {
    Write-ProcessOutput -Stdout $compat.Stdout -Stderr $compat.Stderr
    Set-Result "le-the-forge compatibility reader" "FAIL" "exit code $($compat.ExitCode)"
} else {
    try {
        $compatJson = $compat.Stdout | ConvertFrom-Json
        Set-Result "le-the-forge compatibility reader" "PASS" "compatibility JSON parsed"

        Write-Host "status: $($compatJson.status)"
        Write-Host "bundle_id: $($compatJson.bundle_id)"
        Write-Host "game_version: $($compatJson.game_version)"
        Write-Host "build_number: $($compatJson.build_number)"
        Write-Host "data_patch: $($compatJson.data_patch)"
        Write-Host "validation_status: $($compatJson.validation_status)"
        Write-Host "known_gap_count: $($compatJson.known_gap_count)"

        if ($compatJson.family_summary) {
            Write-Host "family_summary.total: $($compatJson.family_summary.total)"
            Write-Host "family_summary.required_now: $($compatJson.family_summary.required_now)"
            Write-Host "family_summary.deferred: $($compatJson.family_summary.deferred)"
        }

        $blockedCount = if ($compatJson.blocked_families) { @($compatJson.blocked_families).Count } else { 0 }
        $degradedCount = if ($compatJson.degraded_families) { @($compatJson.degraded_families).Count } else { 0 }
        $warningCount = if ($compatJson.warning_families) { @($compatJson.warning_families).Count } else { 0 }
        Write-Host "blocked_families: $blockedCount"
        Write-Host "degraded_families: $degradedCount"
        Write-Host "warning_families: $warningCount"

        $missingJsonFields = @()
        foreach ($field in @("status", "bundle_id", "game_version", "build_number", "data_patch", "validation_status")) {
            if ($null -eq $compatJson.$field -or $compatJson.$field -eq "") {
                $missingJsonFields += $field
            }
        }
        if ($null -eq $compatJson.family_summary) {
            $missingJsonFields += "family_summary"
        }
        if (-not ($compatJson.PSObject.Properties.Name -contains "known_gap_count")) {
            $missingJsonFields += "known_gap_count"
        }

        if ($missingJsonFields.Count -gt 0) {
            Set-Result "compatibility JSON shape" "FAIL" "missing fields: $($missingJsonFields -join ', ')"
        } else {
            Set-Result "compatibility JSON shape" "PASS" "required fields present"
        }

        if ($compatJson.status -eq "compatible_with_warnings") {
            Set-Result "expected status check" "PASS" "current Phase 1 bundle reports compatible_with_warnings"
        } elseif ($compatJson.status -eq "compatible") {
            Set-Result "expected status check" "WARN" "bundle is fully compatible; current Phase 1 bundle is expected to warn"
        } elseif ($compatJson.status -eq "incompatible") {
            Set-Result "expected status check" "FAIL" "bundle is incompatible"
        } else {
            Set-Result "expected status check" "FAIL" "unknown status: $($compatJson.status)"
        }
    } catch {
        Write-ProcessOutput -Stdout $compat.Stdout -Stderr $compat.Stderr
        Set-Result "le-the-forge compatibility reader" "FAIL" "JSON parse failed: $($_.Exception.Message)"
    }
}

Write-Section "Summary"
$Results.GetEnumerator() | ForEach-Object {
    "{0,-38} {1,-5} {2}" -f $_.Key, $_.Value.Status, $_.Value.Message
}

if ($CriticalFailure) {
    Write-Host "Overall result: FAIL"
    exit 1
}

$hasWarning = $false
foreach ($entry in $Results.GetEnumerator()) {
    if ($entry.Value.Status -eq "WARN") {
        $hasWarning = $true
        break
    }
}

if ($hasWarning) {
    Write-Host "Overall result: WARN"
} else {
    Write-Host "Overall result: PASS"
}

exit 0
