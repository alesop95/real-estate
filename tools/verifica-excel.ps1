# Verifica del workbook generato: apre il file con Excel, forza il ricalcolo
# completo, segnala ogni cella in errore e stampa i valori chiave.
#
# Serve perche' openpyxl scrive le formule ma non le valuta: senza questo passaggio
# un errore di sintassi, un nome non risolto o un blocco XML malformato resterebbe
# invisibile fino a quando non apre il file una persona.
#
# Uso: powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1 [percorso]

param(
    [string]$Percorso = "output\Valutazione-Immobile.xlsx"
)

$ErrorActionPreference = "Stop"
$pieno = (Resolve-Path $Percorso).Path
Write-Output "Verifica di $pieno"
Write-Output ""

# Excel espone l'automazione COM nella lingua di installazione: con una console in
# italiano il late binding di PowerShell non risolve i metodi inglesi come Open e
# fallisce con un errore che sembra dire che il metodo non esiste. La chiamata va
# quindi fatta con InvokeMember passando esplicitamente la cultura en-US.
$ci = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")

function Invoca($oggetto, $metodo, $argomenti) {
    return $oggetto.GetType().InvokeMember($metodo, "InvokeMethod", $null, $oggetto, $argomenti, $ci)
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$errori = 0

try {
    $wb = Invoca $excel.Workbooks "Open" @($pieno)
    $excel.CalculateFullRebuild()

    Write-Output "Celle in errore"
    foreach ($ws in $wb.Worksheets) {
        $ur = $ws.UsedRange
        if ($null -eq $ur) { continue }
        $blocco = $null
        # xlCellTypeFormulas = -4123, xlErrors = 16. Solleva eccezione se non trova
        # nulla, che e' il caso buono.
        try { $blocco = $ur.SpecialCells(-4123, 16) } catch { $blocco = $null }
        if ($null -ne $blocco) {
            foreach ($cella in $blocco) {
                Write-Output ("  {0}!{1} = {2}" -f $ws.Name, $cella.Address(0, 0), $cella.Text)
                Write-Output ("      formula: {0}" -f $cella.Formula)
                $errori++
            }
        }
    }
    if ($errori -eq 0) { Write-Output "  nessuna" }

    Write-Output ""
    Write-Output "Valori chiave dopo il ricalcolo"
    $chiavi = @(
        "valore_catastale", "base_registro", "imposte_totali", "valore_bonus",
        "costi_accessori", "costo_totale", "incidenza_costi", "esborso",
        "rata_mensile", "interessi_totali", "oneri_mutuo",
        "ricavo_lordo", "noi_annuo", "utile_locazione"
    )
    foreach ($k in $chiavi) {
        $intervallo = $excel.Range($k)
        Write-Output ("  {0,-24} {1}" -f $k, $intervallo.Text)
    }

    # Le etichette che sono solo numeri appartengono alle tabelle anno per anno e
    # non sono voci di sintesi: si saltano.
    function StampaSintesi($ws, $daRiga, $aRiga) {
        for ($riga = $daRiga; $riga -le $aRiga; $riga++) {
            $etichetta = $ws.Cells.Item($riga, 1).Text
            $valore = $ws.Cells.Item($riga, 2).Text
            if ($etichetta -and $valore -and -not ($etichetta -match '^\s*\d+\s*$')) {
                Write-Output ("  {0,-52} {1}" -f $etichetta, $valore)
            }
        }
    }

    Write-Output ""
    Write-Output "Foglio Locazione, confronto fra regimi"
    $l = $wb.Worksheets.Item("Locazione")
    for ($riga = 1; $riga -le 70; $riga++) {
        $etichetta = $l.Cells.Item($riga, 1).Text
        if ($etichetta -and $l.Cells.Item($riga, 2).Text) {
            Write-Output ("  {0,-46} {1,14} {2,14} {3,14} {4,14}" -f $etichetta,
                $l.Cells.Item($riga, 2).Text, $l.Cells.Item($riga, 3).Text,
                $l.Cells.Item($riga, 4).Text, $l.Cells.Item($riga, 5).Text)
        }
    }

    Write-Output ""
    Write-Output "Foglio Metriche"
    StampaSintesi $wb.Worksheets.Item("Metriche") 4 45

    Write-Output ""
    Write-Output "Foglio Confronto affitto"
    StampaSintesi $wb.Worksheets.Item("Confronto affitto") 45 62

    Invoca $wb "Close" @($false) | Out-Null
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}

Write-Output ""
if ($errori -gt 0) {
    Write-Output "ESITO: $errori celle in errore"
    exit 1
} else {
    Write-Output "ESITO: nessuna cella in errore"
    exit 0
}
