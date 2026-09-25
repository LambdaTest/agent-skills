# kane-cli ready check (preflight). Windows PowerShell 5.1 and later.
#
# Prints, in one call, everything an agent needs to know before it starts a
# kane-cli run. It only reads status. It changes nothing: no sign-in, no
# config write, no install, no network call of its own. It never reads
# credential files. It always exits 0, and problems show up in the text.
# This is the twin of preflight.sh: same sections, same keys, same order.
#
# Usage: powershell -File preflight.ps1 [--mobile emulator|simulator] [--grid]
#
# Output is plain text in "## <section>" blocks, always in this order:
#   version       kane-cli --version, or the word "missing"
#   whoami        kane-cli whoami, then exit=<code>
#   balance       kane-cli balance, then exit=<code>
#   settings      kane-cli config show, then exit=<code>
#   agent-config  saved agent preferences, or the word "none"
#   env           ci= ssh= display= os= arch= node=
#   chrome        found=<path> and override=<KANE_CLI_CHROME_PATH>
#   app           port=<n> for each local dev port with a listener
#   tests         count=<n> of *_test.md files within four directory levels
#   mobile        only with --mobile: kane-cli doctor --target <kind>
#   grid          only with --grid: kane-cli plugin doctor remote-execution
# When kane-cli is missing, every command block holds the word "missing".

$ErrorActionPreference = 'Continue'
$DevPorts = @(3000, 3001, 4200, 4321, 5173, 5174, 8000, 8080, 8888)

# Flags. Unknown ones are ignored. -mobile and -grid work too.
$MobileAsked = $false
$Mobile = ''
$Grid = $false
$i = 0
while ($i -lt $args.Count) {
    $flag = "$($args[$i])"
    $name = $flag.TrimStart('-').ToLowerInvariant()
    if ($flag.StartsWith('-')) {
        if ($name -eq 'grid') {
            $Grid = $true
        } elseif ($name -eq 'mobile') {
            $MobileAsked = $true
            if (($i + 1) -lt $args.Count -and -not "$($args[$i + 1])".StartsWith('-')) {
                $Mobile = "$($args[$i + 1])"
                $i++
            }
        } elseif ($name.StartsWith('mobile=')) {
            $MobileAsked = $true
            $Mobile = $flag.Substring($flag.IndexOf('=') + 1)
        }
    }
    $i++
}
$MobileOk = ($Mobile -ceq 'emulator') -or ($Mobile -ceq 'simulator')

$HaveCli = [bool](Get-Command kane-cli -ErrorAction SilentlyContinue)

# Prints the block body for one kane-cli call: raw output, then exit=<code>.
function Write-CommandBlock {
    param([string[]]$CliArgs)
    if (-not $script:HaveCli) {
        Write-Output 'missing'
        return
    }
    $code = $null
    try {
        & kane-cli @CliArgs 2>&1 | ForEach-Object { "$_" }
        $code = $LASTEXITCODE
    } catch {
        Write-Output "$_"
    }
    if ($null -eq $code) { $code = 1 }
    Write-Output "exit=$code"
}

# Counts *_test.md files. Files in the start folder are level 1.
function Get-TestFileCount {
    param([string]$Dir, [int]$Level)
    $count = 0
    $items = @(Get-ChildItem -LiteralPath $Dir -Force -ErrorAction SilentlyContinue)
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            if ($Level -lt 4 -and $item.Name -ne 'node_modules' -and $item.Name -ne '.git') {
                $count += Get-TestFileCount -Dir $item.FullName -Level ($Level + 1)
            }
        } elseif ($item.Name -like '*_test.md') {
            $count++
        }
    }
    return $count
}

# Read and print UTF-8 so the whoami box survives. Put back at the end.
$PreviousEncoding = $null
try {
    $PreviousEncoding = [Console]::OutputEncoding
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
} catch { }

try {
    Write-Output '## version'
    if ($HaveCli) {
        $version = ''
        try { $version = (& kane-cli --version 2>$null | ForEach-Object { "$_" }) -join "`n" } catch { }
        if (-not $version) {
            try { $version = (& kane-cli --version 2>&1 | ForEach-Object { "$_" }) -join "`n" } catch { }
        }
        Write-Output $version
    } else {
        Write-Output 'missing'
    }

    Write-Output '## whoami'
    Write-CommandBlock -CliArgs @('whoami')

    Write-Output '## balance'
    Write-CommandBlock -CliArgs @('balance')

    Write-Output '## settings'
    Write-CommandBlock -CliArgs @('config', 'show')

    Write-Output '## agent-config'
    $agentConfig = [IO.Path]::Combine($HOME, '.testmuai', 'kaneai', 'agent-config', 'config.json')
    $agentConfigText = $null
    if (Test-Path -LiteralPath $agentConfig -PathType Leaf) {
        try { $agentConfigText = Get-Content -LiteralPath $agentConfig -Raw -Encoding UTF8 -ErrorAction Stop } catch { }
    }
    if ($null -ne $agentConfigText) {
        Write-Output $agentConfigText.TrimEnd("`r", "`n")
    } else {
        Write-Output 'none'
    }

    Write-Output '## env'
    $onWindows = ($env:OS -eq 'Windows_NT')
    $ssh = 'no'
    if ($env:SSH_CONNECTION -or $env:SSH_TTY) { $ssh = 'yes' }
    $display = 'no'
    if ($onWindows -or $IsMacOS) {
        # Windows and macOS always have a screen, unless this is a remote shell.
        if ($ssh -eq 'no') { $display = 'yes' }
    } elseif ($env:DISPLAY -or $env:WAYLAND_DISPLAY) {
        $display = 'yes'
    }
    $osName = 'Windows'
    $arch = "$env:PROCESSOR_ARCHITECTURE"
    if (-not $onWindows) {
        try { $osName = "$(& uname -s 2>$null)" } catch { $osName = '' }
        try { $arch = "$(& uname -m 2>$null)" } catch { $arch = '' }
    }
    $node = ''
    if (Get-Command node -ErrorAction SilentlyContinue) {
        try { $node = "$(& node --version 2>$null)" } catch { }
    }
    Write-Output "ci=$env:CI"
    Write-Output "ssh=$ssh"
    Write-Output "display=$display"
    Write-Output "os=$osName"
    Write-Output "arch=$arch"
    Write-Output "node=$node"

    Write-Output '## chrome'
    $candidates = @($env:KANE_CLI_CHROME_PATH)
    foreach ($base in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
        if ($base) { $candidates += [IO.Path]::Combine($base, 'Google', 'Chrome', 'Application', 'chrome.exe') }
    }
    $candidates += '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    $candidates += '/usr/bin/google-chrome'
    $candidates += '/usr/bin/google-chrome-stable'
    foreach ($commandName in @('chrome', 'google-chrome')) {
        $onPath = Get-Command $commandName -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($onPath) { $candidates += $onPath.Path }
    }
    $found = ''
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            $found = $candidate
            break
        }
    }
    Write-Output "found=$found"
    Write-Output "override=$env:KANE_CLI_CHROME_PATH"

    Write-Output '## app'
    $listening = @()
    try {
        if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
            $listening = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
                ForEach-Object { [int]$_.LocalPort })
        } elseif (Get-Command netstat -ErrorAction SilentlyContinue) {
            # The first address on a LISTEN line is the local one.
            $listening = @(& netstat -an 2>$null | ForEach-Object {
                    if ("$_" -match 'LISTEN' -and "$_" -match '[:.](\d+)\s') { [int]$Matches[1] }
                })
        }
    } catch { }
    foreach ($port in $DevPorts) {
        if ($listening -contains $port) { Write-Output "port=$port" }
    }

    Write-Output '## tests'
    $testCount = 0
    try { $testCount = Get-TestFileCount -Dir (Get-Location).Path -Level 1 } catch { }
    Write-Output "count=$testCount"

    if ($MobileAsked) {
        Write-Output '## mobile'
        if ($MobileOk) {
            Write-CommandBlock -CliArgs @('doctor', '--target', $Mobile)
        } else {
            Write-Output 'invalid target'
        }
    }

    if ($Grid) {
        Write-Output '## grid'
        Write-CommandBlock -CliArgs @('plugin', 'doctor', 'remote-execution')
    }
} catch {
    Write-Output "preflight error: $_"
} finally {
    if ($null -ne $PreviousEncoding) {
        try { [Console]::OutputEncoding = $PreviousEncoding } catch { }
    }
}

exit 0
