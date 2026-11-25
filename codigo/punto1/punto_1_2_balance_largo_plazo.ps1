param(
    [string]$InputPath = '../../datos/punto1/PE_200907_master_monthly_T1_original.csv',
    [string]$OutputDir = '../../productos/punto1'
)

$ErrorActionPreference = 'Stop'
$culture = [System.Globalization.CultureInfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentCulture = $culture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = $culture

function To-Number([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -eq 'NaN') { return $null }
    return [double]::Parse($Value, $culture)
}

$inputFile = Join-Path $PSScriptRoot $InputPath
$outputFolder = Join-Path $PSScriptRoot $OutputDir
New-Item -ItemType Directory -Force -Path $outputFolder | Out-Null

$monthly = Import-Csv -LiteralPath $inputFile | ForEach-Object {
    [PSCustomObject]@{
        date = [datetime]::ParseExact($_.date, 'yyyy-MM-dd', $culture)
        year = [int]$_.date.Substring(0, 4)
        month = [int]$_.date.Substring(5, 2)
        pl_mm_month = To-Number $_.camels_precip_mm_month
        pi_mm_month = To-Number $_.imerg_precip_mm_month
        q_mm_month = To-Number $_.runoff_mm_month
        pl_valid = $_.camels_precip_available -eq 'TRUE'
        pi_valid = $_.imerg_available -eq 'TRUE'
        q_valid = $_.flow_obs_meets_90pct -eq 'TRUE'
    }
}

$validMonthly = $monthly | Where-Object { $_.pl_valid -and $_.pi_valid -and $_.q_valid }
$completeYears = $validMonthly |
    Group-Object year |
    Where-Object { $_.Count -eq 12 } |
    ForEach-Object { [int]$_.Name } |
    Sort-Object

$analysis = $validMonthly | Where-Object { $_.year -in $completeYears }
$annual = foreach ($year in $completeYears) {
    $subset = $analysis | Where-Object { $_.year -eq $year }
    $pl = ($subset | Measure-Object pl_mm_month -Sum).Sum
    $pi = ($subset | Measure-Object pi_mm_month -Sum).Sum
    $q = ($subset | Measure-Object q_mm_month -Sum).Sum
    [PSCustomObject]@{
        year = $year
        pl_mm_year = $pl
        pi_mm_year = $pi
        q_mm_year = $q
        et_l_mm_year = $pl - $q
        et_i_mm_year = $pi - $q
    }
}

$periodParts = [System.Collections.Generic.List[string]]::new()
$rangeStart = $completeYears[0]
$rangeEnd = $completeYears[0]
for ($index = 1; $index -lt $completeYears.Count; $index++) {
    if ($completeYears[$index] -eq ($rangeEnd + 1)) {
        $rangeEnd = $completeYears[$index]
    } else {
        $periodParts.Add($(if ($rangeStart -eq $rangeEnd) { "$rangeStart" } else { "$rangeStart-$rangeEnd" }))
        $rangeStart = $completeYears[$index]
        $rangeEnd = $completeYears[$index]
    }
}
$periodParts.Add($(if ($rangeStart -eq $rangeEnd) { "$rangeStart" } else { "$rangeStart-$rangeEnd" }))
$periodLabel = $periodParts -join ';'
$summary = [PSCustomObject]@{
    period = $periodLabel
    complete_calendar_years = $completeYears.Count
    pl_mm_year = ($annual | Measure-Object pl_mm_year -Average).Average
    pi_mm_year = ($annual | Measure-Object pi_mm_year -Average).Average
    q_mm_year = ($annual | Measure-Object q_mm_year -Average).Average
    et_l_mm_year = ($annual | Measure-Object et_l_mm_year -Average).Average
    et_i_mm_year = ($annual | Measure-Object et_i_mm_year -Average).Average
}

$monthNames = @('Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre')
$climatology = foreach ($month in 1..12) {
    $subset = $analysis | Where-Object { $_.month -eq $month }
    [PSCustomObject]@{
        month = $month
        month_name = $monthNames[$month - 1]
        observations = $subset.Count
        pl_mm_month = ($subset | Measure-Object pl_mm_month -Average).Average
        pi_mm_month = ($subset | Measure-Object pi_mm_month -Average).Average
        q_mm_month = ($subset | Measure-Object q_mm_month -Average).Average
    }
}

$hydrologicalYears = foreach ($endYear in 2001..2023) {
    $startYear = $endYear - 1
    $subset = $monthly | Where-Object {
        ($_.year -eq $startYear -and $_.month -ge 9) -or
        ($_.year -eq $endYear -and $_.month -le 8)
    } | Sort-Object date

    $plValid = @($subset | Where-Object pl_valid)
    $piValid = @($subset | Where-Object pi_valid)
    $qValid = @($subset | Where-Object q_valid)
    $missingQ = @($subset | Where-Object { -not $_.q_valid } | ForEach-Object { $_.date.ToString('yyyy-MM', $culture) })
    $plAnnual = if ($plValid.Count -eq 12) { ($plValid | Measure-Object pl_mm_month -Sum).Sum } else { $null }
    $piAnnual = if ($piValid.Count -eq 12) { ($piValid | Measure-Object pi_mm_month -Sum).Sum } else { $null }
    $qAnnual = if ($qValid.Count -eq 12) { ($qValid | Measure-Object q_mm_month -Sum).Sum } else { $null }

    [PSCustomObject]@{
        hydrological_year = "AH $endYear"
        period = "$startYear-09 a $endYear-08"
        pl_mm_year = $plAnnual
        pi_mm_year = $piAnnual
        q_mm_year = $qAnnual
        et_l_mm_year = if ($null -ne $plAnnual -and $null -ne $qAnnual) { $plAnnual - $qAnnual } else { $null }
        et_i_mm_year = if ($null -ne $piAnnual -and $null -ne $qAnnual) { $piAnnual - $qAnnual } else { $null }
        pl_valid_months = $plValid.Count
        pi_valid_months = $piValid.Count
        q_valid_months = $qValid.Count
        status = if ($plValid.Count -eq 12 -and $piValid.Count -eq 12 -and $qValid.Count -eq 12) { 'Completo' } else { 'Incompleto' }
        missing_q_months = if ($missingQ.Count -gt 0) { $missingQ -join ';' } else { '' }
    }
}

$annual | Export-Csv -LiteralPath (Join-Path $outputFolder 'punto_1_2_totales_anuales_periodo_comun.csv') -NoTypeInformation -Encoding utf8
$summary | Export-Csv -LiteralPath (Join-Path $outputFolder 'punto_1_2_balance_largo_plazo_resumen.csv') -NoTypeInformation -Encoding utf8
$climatology | Export-Csv -LiteralPath (Join-Path $outputFolder 'punto_1_2_climatologia_mensual_periodo_comun.csv') -NoTypeInformation -Encoding utf8
$hydrologicalYears | Export-Csv -LiteralPath (Join-Path $outputFolder 'punto_1_2_anios_hidrologicos_sep_ago.csv') -NoTypeInformation -Encoding utf8

$summary
$climatology
$hydrologicalYears
