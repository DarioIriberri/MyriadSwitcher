Set-ExecutionPolicy RemoteSigned

#####################################################################################################################################################################################################################
############################################      Configuration      ################################################################################################################################################
#####################################################################################################################################################################################################################
#mode con: cols=236 lines=1000

$scryptBatchFile 	= "E:\Litecoin\SGMiner\cgminer-startup.........................MYR - Switch.bat"
$groestlBatchFile 	= "E:\SPH-SGMINER\cgminer-startup.........................MYRG - Switch.bat"
$skeinBatchFile 	= "E:\Skein\cgminer-startup.........................MYR - Switch.bat"
$qubitBatchFile 	= "E:\SPH-SGMINER\cgminer-startup.........................MYRQ - Switch.bat"

$logPath = "C:\Dropbox\Public\Myriad_log"

$scryptHashRate  = 1.38		# Your scrypt hashrate 	(MH/s)
$groestlHashRate = 22.1		# Your groestl hashrate	(MH/s)
$skeinHashRate   = 418		# Your skein hashrate 	(MH/s)
$qubitHashRate   = 10		# Your qubit hashrate	(MH/s)

$scryptWatts	= 650
$groestlWatts	= 340
$skeinWatts		= 550
$qubitWatts		= 360

$sleepSHORT = 3				# Time to sleep (in minutes) while on the same algo as the previous iteration																							
$sleepLONG  = 5					# Time to sleep (in minutes) after switching algos
$hysteresis = 1.05				# Hysteresis factor. Won't switch to a new algo until it exceeds the current one by this factor. Avoids frantic switching back and forth when two algos constantly alternate on top
$minTimeNoHysteresis = 99999	# Hysteresis time threshold in minutes. Hysteresis factor will be ignored when the current algo has been running for more than this many minutes

$rampUptime = 10

$scryptFactor	= 1.0
$groestlFactor	= 0.0
$skeinFactor	= 1.0
$qubitFactor	= 1.0

$timeout = 30000 # 30 secs

$maxErrors = 2

$sleepSHORTDebug = 30 # seconds
$sleepLONGDebug  = 30 # seconds

$debug = 1

$MODE_MAX_PER_DAY = 1
$MODE_MAX_PER_WATT = 2
$MODE_MAX_PER_HYBRID = 3

#####################################################################################################################################################################################################################
###########################################        Functions         ################################################################################################################################################
#####################################################################################################################################################################################################################

function printheader ( ) {
	write-host " " 

	write-host "Time     Elapsed/Stint  Algo     Exch  Prof 1Mh/s   My profit   Scrypt coins  /day   Groestl coins /day   Skein coins   /day   Qubit coins   /day  Tot.Coins     Tot.$   /day   Prof 1Mh/s   My profit  Watts   C/W" -foreground "Cyan" -background "Black"
			   #17:22:03 00 00:00:00 >  Groestl  525 $   598043 $ >  825300 $   S     0   0%  1227   G     0 100%  1572   K     0   0%  1048   Q     0   0%  1222       0          0 $   1572     598043 $ >  825300 $   340W  2.123
}

function getProcess ( $procName ) { 
	return ( Get-Process $procName -ErrorAction SilentlyContinue )
}

function printData ( $status, $now, $globalTime, $switchtext, $currentPrice, $valCorrected, $spacerColor, $coins, $wattsAvg, $active, $stopped ) {
	$totalCoinsFormated = ( formatDecimal $coins 0 )
	
	$totalSatoshi = $coins * $currentPrice
	$dailyCoinsTot = 0
	$profitabilityTotal = 0
	
	if ( $globalTime -gt 0 ) {
		$dailyCoinsTot = $coins * ( $ticksPerDay / $globalTime )
		$profitabilityTotal = $totalSatoshi * ( $ticksPerDay / $globalTime )
	} 
	
	$totalSatoshiStr = formatDecimal ( $totalSatoshi ) 0
	$dailyCoinsFormated = ([string][int]$dailyCoinsTot).padLeft(4)
	
	if ( $status -eq "SWITCH" ) {
	
		$zeroValString = "----"
		
		switch ($active) { 
			$scryptS {
				$totalCoinsScrypt = $coins
				$totalCoinsGroestl = 0
				$totalCoinsSkein   = 0
				$totalCoinsQubit   = 0
				
				$valCorrectedY = $dailyCoinsFormated
				$valCorrectedG = $zeroValString
				$valCorrectedS = $zeroValString
				$valCorrectedQ = $zeroValString
				
				$totalTimeScrypt  = $globalTime
				$totalTimeGroestl = 0
				$totalTimeSkein   = 0
				$totalTimeQubit   = 0
				
			} 
			$groestlS {
				$totalCoinsScrypt = 0
				$totalCoinsGroestl = $coins
				$totalCoinsSkein   = 0
				$totalCoinsQubit   = 0
				
				$valCorrectedY = $zeroValString
				$valCorrectedG = $dailyCoinsFormated
				$valCorrectedS = $zeroValString
				$valCorrectedQ = $zeroValString
				
				$totalTimeScrypt  = 0
				$totalTimeGroestl = $globalTime
				$totalTimeSkein   = 0
				$totalTimeQubit   = 0
				
			} 
			$skeinS {
				$totalCoinsScrypt = 0
				$totalCoinsGroestl = 0
				$totalCoinsSkein   = $coins
				$totalCoinsQubit   = 0
				
				$valCorrectedY = $zeroValString
				$valCorrectedG = $zeroValString
				$valCorrectedS = $dailyCoinsFormated
				$valCorrectedQ = $zeroValString
				
				$totalTimeScrypt  = 0
				$totalTimeGroestl = 0
				$totalTimeSkein   = $globalTime
				$totalTimeQubit   = 0
				
			} 
			$qubitS {
				$totalCoinsScrypt = 0
				$totalCoinsGroestl = 0
				$totalCoinsSkein   = 0
				$totalCoinsQubit   = $coins
				
				$valCorrectedY = $zeroValString
				$valCorrectedG = $zeroValString
				$valCorrectedS = $zeroValString
				$valCorrectedQ = $dailyCoinsFormated
				
				$totalTimeScrypt  = 0
				$totalTimeGroestl = 0
				$totalTimeSkein   = 0
				$totalTimeQubit   = $globalTime
			} 
		}
			
	} else {
		$totalCoinsScrypt = $hashtableCoins.Get_Item($scryptS)
		$totalCoinsGroestl = $hashtableCoins.Get_Item($groestlS)
		$totalCoinsSkein   = $hashtableCoins.Get_Item($skeinS)
		$totalCoinsQubit   = $hashtableCoins.Get_Item($qubitS)
		
		$valCorrectedY = "{0:f0}" -f $hashtableCorrected.Get_Item($scryptS)
		$valCorrectedG = "{0:f0}" -f $hashtableCorrected.Get_Item($groestlS)
		$valCorrectedS = "{0:f0}" -f $hashtableCorrected.Get_Item($skeinS)
		$valCorrectedQ = "{0:f0}" -f $hashtableCorrected.Get_Item($qubitS)	
		
		$totalTimeScrypt = $hashtableTime.Get_Item($scryptS)
		$totalTimeGroestl = $hashtableTime.Get_Item($groestlS)
		$totalTimeSkein   = $hashtableTime.Get_Item($skeinS)
		$totalTimeQubit   = $hashtableTime.Get_Item($qubitS)
	}
	
	$stringOthersCoinsY = " S " + ( formatDecimal $totalCoinsScrypt 0 ).padLeft(5) + " " + (formatPct $totalCoinsScrypt $coins 0).padLeft(4) + " " + $valCorrectedY.padLeft(5)
	$stringOthersCoinsG = " G " + ( formatDecimal $totalCoinsGroestl 0 ).padLeft(5) + " " + (formatPct $totalCoinsGroestl $coins 0).padLeft(4) + " " + $valCorrectedG.padLeft(5)
	$stringOthersCoinsS = " K " + ( formatDecimal $totalCoinsSkein 0 ).padLeft(5) + " " + (formatPct $totalCoinsSkein $coins 0).padLeft(4)+ " " + $valCorrectedS.padLeft(5)
	$stringOthersCoinsQ = " Q " + ( formatDecimal $totalCoinsQubit 0 ).padLeft(5) + " " + (formatPct $totalCoinsQubit $coins 0).padLeft(4) + " " + $valCorrectedQ.padLeft(5)
	
	$stringPrice = ([string][int](($currentPrice * $valCorrected) / $scryptHashRate)).padLeft(8) + " `$ -" + ([string]($currentPrice * $valCorrected)).padLeft(8) + " `$" 
	
	$fcY = $fcG = $fcS = $fcQ = $hashColorF3.Get_Item($status)
	$bcY = $bcG = $bcS = $bcQ = $hashColorB3.Get_Item($status)
	
	if ( $active -eq $scryptS ) {
		$fcY = $foregroundActive
	}
	
	if ( $active -eq $groestlS ) {
		$fcG = $foregroundActive
	}
	
	if ( $active -eq $skeinS ) {
		$fcS = $foregroundActive
	}
	
	if ( $active -eq $qubitS ) {
		$fcQ = $foregroundActive
	}
	
	if ( ! $scryptFactor ) {
		$fcY = $foregroundDisabled
		#$bcY = $backgroundDisabled
	}

	if ( ! $groestlFactor ) {
		$fcG = $foregroundDisabled
		#$bcG = $backgroundDisabled
	}

	if ( ! $skeinFactor ) {
		$fcS = $foregroundDisabled
		#$bcS = $backgroundDisabled
	}

	if ( ! $qubitFactor ) {
		$fcQ = $foregroundDisabled
		#$bcQ = $backgroundDisabled
	}
	
	if ( $stopped -and $status -ne "SWITCH" ) {
		$fcY = $fcG = $fcS = $fcQ = $tforeground = $foregroundDisabled
		
	} else {
		$tforeground = $hashColorF2.Get_Item($status)
	}
	
	$totals = "  " + $totalSatoshiStr.toString().padLeft(9) + " `$   " + $dailyCoinsFormated + "   " + ([string][int]( $profitabilityTotal / $scryptHashRate )).padLeft(8) + " `$ -" + ([string][int]$profitabilityTotal).padLeft(8) + " `$  "  
	
	$currentPriceFormated = ([string]$currentPrice).padLeft(4)
	$coinsPerWatt = "{0:f2}" -f ( $dailyCoinsFormated / [decimal]$wattsAvg )
	
	#Write-Host ( ([string]$time) + " " ) 													-background $hashColorB1.Get_Item($status) 	-foreground $hashColorF1.Get_Item($status) -nonewline
	Write-Host ( ( $now.toString("HH:mm:ss") ) + " " + ( formatTimeTicks( $globalTime ) ) + " " ) 								-background $hashColorB1.Get_Item($status) 	-foreground $hashColorF1.Get_Item($status) 	-nonewline
	Write-Host ( $switchtext ) 	 	-background $hashColorB2.Get_Item($status) 	-foreground $tforeground 	-nonewline
	Write-Host ( " " + $currentPriceFormated + " `$" )	 				-background $hashColorB2.Get_Item($status) 	-foreground $priceForegroundColor 	-nonewline
	Write-Host ( " " + $stringPrice + " " ) 	-background $hashColorB2.Get_Item($status) 	-foreground $tforeground 	-nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( "" + $stringOthersCoinsY + " " ) 									-background $bcY 							-foreground $fcY 							-nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( "" + $stringOthersCoinsG + " " ) 									-background $bcG 							-foreground $fcG 							-nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( "" + $stringOthersCoinsS + " " ) 									-background $bcS 							-foreground $fcS 							-nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( "" + $stringOthersCoinsQ + " " ) 									-background $bcQ 							-foreground $fcQ 							-nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( " " + ([string]$totalCoinsFormated).padLeft(5) + $totals ) 														-background $hashColorB4.Get_Item($status) 	-foreground $hashColorF4.Get_Item($status)  -nonewline
	Write-Host ( " " + [int]$wattsAvg + "W ") 												-background $hashColorB1.Get_Item($status) 	-foreground $hashColorF1.Get_Item($status) -nonewline
	Write-Host ( " " ) -background $spacerColor -nonewline
	Write-Host ( " " + $coinsPerWatt.padLeft(2) + " " )											-background $hashColorB1.Get_Item($status) 	-foreground $hashColorF1.Get_Item($status) 
	
	$htmlTime = 0
	
	if ( $logActive ) {
		$startT = get-date
		$file = Get-Content ( $fileName + ".txt" )
		$html = @()
		Foreach ($line in $file) {
			$line = $line -replace " ", "&nbsp;"
			$myObject = New-Object -TypeName PSObject
			Add-Member -InputObject $MyObject -Type NoteProperty -Name $fileName -Value $line
			$html += $myObject
		}
		
		$head = "<style>BODY{background-color:#181818;color:#D5D5D5;font-family:""Courier New"";font-weight:bold;font-size:95%;}table{border-collapse:collapse;width:1880px;}tr{line-height:1}div:{margin-bottom:20px;}</style>"
		$head += ( "<script>window.onload=function(){setTimeout(function() { location.reload();document.getElementById( 'bottom' ).scrollIntoView();}," + ( $sleepSHORT * 1000 ) + ")}</script>" )
		#$head += ( "<META HTTP-EQUIV=`"refresh`" CONTENT=""" + $sleepSHORT + """>" )
		
		$html = $html | ConvertTo-Html -Property $fileName -head $head -body "<H2>Myriad Switcher</H2>" 
		$htmlDec = [System.Web.HttpUtility]::HtmlDecode( $html )
		$htmlDec = $htmlDec -replace "</body></html>", "<div id=""bottom""/></body></html>"
		
		$htmlDec | Out-File ( $fileName + ".html" )
		
		$htmlTime = (new-timespan $startT $(Get-Date)).totalSeconds	
	}
	
	return $htmlTime
}

function loadConfig ( $skeinFactor) {
	$file = Get-Content ( "myriadSwitcher.conf" )
	$obj = $ser.DeserializeObject($file)
	
	$globalCorrectionFactor = [decimal]$obj.get_item("globalCorrectionFactor")
	
	Set-Variable -Name scryptBatchFile 		-Value ( "'" + $obj.get_item("scryptBatchFile") + "'" ) -Scope 1
	Set-Variable -Name groestlBatchFile  	-Value ( "'" + $obj.get_item("groestlBatchFile") + "'" ) -Scope 1
	Set-Variable -Name skeinBatchFile 		-Value ( "'" + $obj.get_item("skeinBatchFile") + "'" ) -Scope 1
	Set-Variable -Name qubitBatchFile   	-Value ( "'" + $obj.get_item("qubitBatchFile") + "'" ) -Scope 1
	Set-Variable -Name logActive      		-Value $obj.get_item("logActive") -Scope 1
	Set-Variable -Name logPath      		-Value $obj.get_item("logPath") -Scope 1
	Set-Variable -Name mode      			-Value $obj.get_item("mode") -Scope 1
	Set-Variable -Name sleepSHORT     		-Value $obj.get_item("sleepSHORT") -Scope 1
	Set-Variable -Name sleepLONG   			-Value $obj.get_item("sleepLONG") -Scope 1
	Set-Variable -Name hysteresis  			-Value ([decimal]$obj.get_item("hysteresis") / 100 + 1) -Scope 1
	Set-Variable -Name minTimeNoHysteresis  -Value $obj.get_item("minTimeNoHysteresis") -Scope 1
	Set-Variable -Name rampUptime  			-Value $obj.get_item("rampUptime") -Scope 1
	Set-Variable -Name scryptHashRate  		-Value (( $obj.get_item("scryptHashRate")) * $globalCorrectionFactor )-Scope 1
	Set-Variable -Name groestlHashRate  	-Value (( $obj.get_item("groestlHashRate")) * $globalCorrectionFactor ) -Scope 1
	Set-Variable -Name skeinHashRate  		-Value (( $obj.get_item("skeinHashRate")) * $globalCorrectionFactor ) -Scope 1
	Set-Variable -Name qubitHashRate 		-Value (( $obj.get_item("qubitHashRate")) * $globalCorrectionFactor ) -Scope 1
	Set-Variable -Name scryptWatts 			-Value $obj.get_item("scryptWatts") -Scope 1
	Set-Variable -Name groestlWatts  		-Value $obj.get_item("groestlWatts") -Scope 1
	Set-Variable -Name skeinWatts  			-Value $obj.get_item("skeinWatts") -Scope 1
	Set-Variable -Name qubitWatts  			-Value $obj.get_item("qubitWatts") -Scope 1
	Set-Variable -Name idleWatts  			-Value $obj.get_item("idleWatts") -Scope 1
	Set-Variable -Name scryptFactor 		-Value $obj.get_item("scryptFactor") -Scope 1
	Set-Variable -Name groestlFactor  		-Value $obj.get_item("groestlFactor") -Scope 1
	Set-Variable -Name skeinFactor 			-Value $obj.get_item("skeinFactor") -Scope 1
	Set-Variable -Name qubitFactor 			-Value $obj.get_item("qubitFactor") -Scope 1
	Set-Variable -Name minCoins 			-Value $obj.get_item("minCoins") -Scope 1
	#Set-Variable -Name minCoinsPerWatt 		-Value $obj.get_item("minCoinsPerWatt") -Scope 1
	Set-Variable -Name attenuation 			-Value $obj.get_item("attenuation") -Scope 1
	Set-Variable -Name timeout 				-Value ([int]$obj.get_item("timeout") * 1000) -Scope 1
	Set-Variable -Name maxErrors  			-Value $obj.get_item("maxErrors") -Scope 1
	Set-Variable -Name sleepSHORTDebug  	-Value $obj.get_item("sleepSHORTDebug") -Scope 1
	Set-Variable -Name sleepLONGDebug 		-Value $obj.get_item("sleepLONGDebug") -Scope 1
	Set-Variable -Name exchange  			-Value $obj.get_item("exchange") -Scope 1
	Set-Variable -Name debug  				-Value $obj.get_item("debug") -Scope 1
	
	Set-Variable -Name hashtableFactors -Value @{ $scryptS = $obj.get_item("scryptFactor"); $groestlS = $obj.get_item("groestlFactor"); $skeinS  = $obj.get_item("skeinFactor"); $qubitS = $obj.get_item("qubitFactor") } -Scope 1
}

function minerStopped ( $current, $miner, $numThreadsPrev, $cpu1, $cpu2 ) {
	if ( $debug ) {
		return 0
	}
	
	$proc = getProcess $miner
	
	if ( ( $proc -eq $null ) -or ( ( @($proc).length ) -eq 0 ) ) {
		return 1	
	} 
	
	$numThreadsNew  =  @(Get-Process -Name $miner*).length
	$stopped = 0
		
	if ( $numThreadsNew -lt $numThreadsPrev ) {
		$stopped = 1
	}
	
	for ($i=0; $i -lt $cpu1.length; $i++) {
		#$dateF = Get-Date -format "dd/MM/yyyy HH:mm:ss"
		#$outS = $dateF + " ... Thread #" + $i + " - Before: " + $cpu1[$i] + " --- After: " + $cpu2[$i]
		
		if ( $cpu1[$i] -eq $cpu2[$i]) {
			$stopped = 1
			
		} 
		#else {
		#	Write-Host $outS + "... RUNNING" $current "OK @ " $newValOriginal -foreground "green"
		#}
	}
	
	return $stopped 
}

function httpGet( $url, $timeout ) {
	$myHttpWebRequest = [system.net.WebRequest]::Create( $url )
	$myHttpWebRequest.Timeout = $timeout
	$myHttpWebRequest.AuthenticationLevel = "None"
	$myHttpWebResponse = $myHttpWebRequest.GetResponse()
	$sr = New-Object System.IO.StreamReader($myHttpWebResponse.GetResponseStream())
	
	#while ( ( $line = $sr.ReadLine() ) -and ! ( $line.contains( "<td valign=middle align=center>77</td>" ) ) ) {
	#while ( $line = $sr.ReadLine() ) {
	#	write-host ("line = " + $line)
	#	$result += $line
	#}
	
	$result = $sr.ReadToEnd();
	
	return $result
}

function getTotalHashValues ( $hash  ) {
	$total
	foreach ($h in $hash.GetEnumerator()) {
		$total = $total + ($h.value)
	}
		
	return [decimal]$total
}

function getAverageHashValues ( $hash  ) {
	$total = getTotalHashValues $hash
		
	return ( $total[1] / $hash.count )
}

function formatTimeSpan( $timeS ) {
	return ( '{0:00} {1:00}:{2:00}:{3:00}' -f $timeS.Days, $timeS.Hours, $timeS.Minutes, $timeS.Seconds ) 
}

function formatTimeTicks( $ticks ) {
	$timeS = ([timespan]$ticks)
	return ( '{0:00} {1:00}:{2:00}:{3:00}' -f $timeS.Days, $timeS.Hours, $timeS.Minutes, $timeS.Seconds ) 
}

function formatDecimal ( $decim, $decDigits ) {	
	return "{0:F$decDigits}" -f [decimal]$decim 
}

function formatPct ( $decim1, $decim2, $decDigits ) { 
	if ( ! $decim2 ) {
		return "{0:N$decDigits}" -f ( 0 ) + "%"
	}
	return "{0:N$decDigits}" -f ( ( ([decimal]$decim1) / ([decimal]$decim2)) * 100 ) + "%" 
}

function killMiner( $miner ) {
	$proc = getProcess $miner
	
	if( $proc -eq $null ) {
		return	
	} else {
		if ( ( @($proc).length ) -gt 0 ) {
			#taskkill /im $miner /f	
			stop-process -ProcessName $miner -Force
		}
	}
}

#####################################################################################################################################################################################################################
#####################################################################################################################################################################################################################
#####################################################################################################################################################################################################################
$scryptS  = " Scrypt "
$groestlS = " Groestl"
$skeinS   = " SKein  "
$qubitS   = " Qubit  "

[System.Reflection.Assembly]::LoadWithPartialName("System.Web.Extensions")
$ser = New-Object System.Web.Script.Serialization.JavaScriptSerializer
cls	
	
loadConfig ( $skeinFactor )

$first = 1

$i=1

$ErrorActionPreference="SilentlyContinue"
Stop-Transcript | out-null
$ErrorActionPreference = "Continue"
$fileSuffix = Get-Date -format "yyyy-MM-dd-HHmmss"

if ( $debug ) {
	$fileSuffix = "debug-" + $fileSuffix
}

$fileName = ($logPath + "\" + $fileSuffix)

if ( $logActive ) {
	Start-Transcript -path ( $fileName + ".txt" ) -append
}

$ticksPerDay = (new-timespan -days 1).ticks
$ticksPerSec = (new-timespan -seconds 1).ticks

write-host " "
write-host "Init time: " ( Get-Date -format "dd-MM-yyyy HH:mm:ss" ) -foreground "white"

$globalStopped = $TRUE

if ( $debug ) {
	write-host " "
	
	Write-Host "########################################################################################################################" -foreground "Yellow"
	Write-Host "#####################################             DEBUG     MODE           #############################################" -foreground "Yellow"
	Write-Host "########################################################################################################################" -foreground "Yellow"

} 

write-host " "

$sleepTime = $sleepLONG
$greaterThanHys = 1
$greaterThanMin = 1

$hashtableTime  = @{ $scryptS = 0; $groestlS = 0; $skeinS = 0; $qubitS = 0 }
$hashtableCoins = @{ $scryptS = 0; $groestlS = 0; $skeinS = 0; $qubitS = 0 }
$watts = 0

#"Black, DarkBlue, DarkGreen, DarkCyan, DarkRed, DarkMagenta, DarkYellow, Gray, DarkGray,Blue, Green, Cyan, Red, Magenta, Yellow, White".

#$hashColorF1  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
#$hashColorF2  = @{ "SWITCH" = "White"; 		"OK" = "Black"; 		"FAIL" = "White"}
#$hashColorF3  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
#$hashColorF4  = @{ "SWITCH" = "White"; 		"OK" = "Black"; 		"FAIL" = "White"}
#$hashColorB1  = @{ "SWITCH" = "Black"; 		"OK" = "DarkGray"; 			"FAIL" = "DarkMagenta"}
#$hashColorB2  = @{ "SWITCH" = "DarkBlue"; 	"OK" = "White"; 		"FAIL" = "DarkRed"}
#$hashColorB3  = @{ "SWITCH" = "Black"; 		"OK" = "DarkGray"; 		"FAIL" = "DarkMagenta"}
#$hashColorB4  = @{ "SWITCH" = "DarkBlue"; 	"OK" = "White"; 		"FAIL" = "DarkRed"}

#$foregroundActive  = "Green"
#$foregroundDisabled = "Gray"
#$spacerColor = "Black" 

$hashColorF1  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
$hashColorF2  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
$hashColorF3  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
$hashColorF4  = @{ "SWITCH" = "White"; 		"OK" = "White"; 		"FAIL" = "White"}
$hashColorB1  = @{ "SWITCH" = "DarkCyan"; 		"OK" = "DarkBlue"; 		"FAIL" = "DarkRed"}
$hashColorB2  = @{ "SWITCH" = "DarkGreen"; 	"OK" = "Black"; 		"FAIL" = "DarkMagenta"}
$hashColorB3  = @{ "SWITCH" = "DarkCyan"; 		"OK" = "DarkBlue"; 		"FAIL" = "DarkRed"}
$hashColorB4  = @{ "SWITCH" = "DarkGreen"; 	"OK" = "Black"; 		"FAIL" = "DarkMagenta"}

$foregroundActive  = "Green"
$foregroundDisabled = "DarkGray"
$spacerColor = "Black" 

$stopwatch = New-Object System.Diagnostics.Stopwatch

$hashtableMiners = @{ $scryptS = "sgminer"; $groestlS = "sgminer"; $skeinS  = "cgminer"; $qubitS = "sgminer" }

$errors = 0
$num = 20.11656761

$pshost = get-host
$pswindow = $pshost.ui.rawui
$newsize = $pswindow.windowsize
$newsize.width = 236
$newsize.height = 59
$pswindow.windowsize = $newsize
$newsize = $pswindow.buffersize
$newsize.width = 236
$newsize.height = 3000
$pswindow.buffersize = $newsize

while($true) {
	
	if ( ! $debug ) {
		$sleepSHORT *= 60																				
		$sleepLONG  *= 60
	
	} else {
		$sleepSHORT = $sleepSHORTDebug 
		$sleepLONG  = $sleepLONGDebug
	}
	
	$startT2 = get-date

	$scryptFactor	= $hashtableFactors.get_item( $scryptS )
	$groestlFactor	= $hashtableFactors.get_item( $groestlS )
	$skeinFactor	= $hashtableFactors.get_item( $skeinS )
	$qubitFactor	= $hashtableFactors.get_item( $qubitS )
	
	try {
		$getResult = httpGet ( "http://myriad.theblockexplorer.com/api.php?mode=info" ) $timeout
		
	} catch {
		Write-Host "Something went wrong while retrieving the difficulties from the block chain explorer       :-(   " -foreground "red"
		#sleep 20
		#continue;
	}
	
	try {
		$getResultCoins = httpGet ( "http://myriad.theblockexplorer.com/api.php?mode=coins" ) $timeout
		
	} catch {
		Write-Host "Something went wrong while retrieving the block reward data from the block chain explorer  :-(   " -foreground "red"
		#sleep 20
		#continue;
	}
	
	try {
		if ( "poloniex" -eq $exchange ) {
			$getResultPrice = httpGet ( "https://poloniex.com/public?command=returnTicker" ) $timeout
		} 
		
		if ( "mintpal" -eq $exchange ) {
			$getResultPrice = httpGet ( "https://api.mintpal.com/v1/market/stats/MYR/BTC" ) $timeout
		} 
		
		$priceOK = 1
	
	} catch {
		#Write-Host "Something went wrong while retrieving the exchange rate data :-(                                                                                                                                                          " -foreground "white" -background "black"
		$currentPrice = 0
		$priceOK = 0
	}
	
	$httpTime = (new-timespan $startT2 $(Get-Date)).totalSeconds	
	
	if ( $debug ) { 
		$i = $i + 1
	}
	
	$obj = $ser.DeserializeObject($getResult)
	$objCoins = $ser.DeserializeObject($getResultCoins)
	$objPrice = $ser.DeserializeObject($getResultPrice)
	
	$diffScrypt 	= $obj.get_item("difficulty_scrypt")
	$diffGroestl 	= $obj.get_item("difficulty_groestl")
	$diffSkein		= $obj.get_item("difficulty_skein")
	$diffQubit      = $obj.get_item("difficulty_qubit")
	
	$per = $objCoins.get_item("per")
	
	$scryptCorrFactor  = $scryptHashRate  * $num * $per
	$groestlCorrFactor = $groestlHashRate * $num * $per
	$skeinCorrFactor   = $skeinHashRate   * $num * $per
	$qubitCorrFactor   = $qubitHashRate   * $num * $per
	
	#$prog = [regex]::matches($getResult,'<td><center>(&nbsp;)*(.*?)(&nbsp;)*<br><br>Coins/Scrypt MH:')
	
	#$diffScrypt 	= [decimal] ( $prog[0].groups[2].value )
	#$diffGroestl 	= [decimal] ( $prog[1].groups[2].value )
	#$diffSkein		= [decimal] ( $prog[2].groups[2].value )
	#$diffQubit      = [decimal] ( $prog[3].groups[2].value )
	
	#$progPrice = [regex]::matches($getResultPrice,'<th>([^<]*)')
	
	$previousPrice = $currentPrice
	
	if ( $priceOK ) {
		if ( "poloniex" -eq $exchange ) {
			[int]$currentPrice = [decimal]($objPrice.get_item("BTC_MYR").get_item("last")) * 100000000			
		} 
		
		if ( "mintpal" -eq $exchange ) {
			[int]$currentPrice = [decimal]($objPrice[0].get_item("last_price")) * 100000000
		}
	}
	
	$prevHashtableCorrected = $hashtableCorrected
	
	if ( $mode -eq $MODE_MAX_PER_WATT ) {
		$attenuation = 0
	}
	
	$hashtableWatts = @{ $scryptS = $scryptWatts; $groestlS = $groestlWatts; $skeinS = $skeinWatts; $qubitS = $qubitWatts }
	$attenuationWatts = [Math]::Pow( (getAverageHashValues $hashtableWatts), (1 / 500)) 
	$attenuationWatts = [Math]::Pow($attenuationWatts, $attenuation)
	$hashtableWattsAttenuated = @{ $scryptS = $scryptWatts + $attenuationWatts; $groestlS = $groestlWatts + $attenuationWatts; $skeinS = $skeinWatts + $attenuationWatts; $qubitS = $qubitWatts + $attenuationWatts }

	#$hashtableOriginal = @{ $scryptS = [decimal][string]$prog[0].groups[1]; $groestlS = [decimal][string]$prog[1].groups[1]; $skeinS = [decimal][string]$prog[2].groups[1]; $qubitS = [decimal][string]$prog[3].groups[1] }
	$hashtableFactored  = @{ $scryptS = (($scryptCorrFactor / $diffScrypt) * $scryptFactor); $groestlS = (($groestlCorrFactor / $diffGroestl) * $groestlFactor); $skeinS = (($skeinCorrFactor / $diffSkein) * $skeinFactor); $qubitS = (($qubitCorrFactor / $diffQubit) * $qubitFactor) }
	$hashtablePerWatt   = @{ $scryptS = (($scryptCorrFactor / $diffScrypt) * $scryptFactor) / $hashtableWatts.get_item($scryptS); $groestlS = (($groestlCorrFactor / $diffGroestl) * $groestlFactor) / $hashtableWatts.get_item($groestlS); $skeinS = (($skeinCorrFactor / $diffSkein) * $skeinFactor) / $hashtableWatts.get_item($skeinS); $qubitS = (($qubitCorrFactor / $diffQubit) * $qubitFactor) / $hashtableWatts.get_item($qubitS) }
	$hashtablePerWattAttenuated   = @{ $scryptS = (($scryptCorrFactor / $diffScrypt) * $scryptFactor) / ( $hashtableWatts.get_item($scryptS) + $attenuationWatts ); $groestlS = (($groestlCorrFactor / $diffGroestl) * $groestlFactor) / ( $hashtableWatts.get_item($groestlS) + $attenuationWatts ); $skeinS = (($skeinCorrFactor / $diffSkein) * $skeinFactor) / ( $hashtableWatts.get_item($skeinS) + $attenuationWatts ); $qubitS = (($qubitCorrFactor / $diffQubit) * $qubitFactor) / ( $hashtableWatts.get_item($qubitS) + $attenuationWatts ) }
	$hashtableCorrected = @{ $scryptS = ($scryptCorrFactor / $diffScrypt); $groestlS = ($groestlCorrFactor / $diffGroestl); $skeinS = ($skeinCorrFactor / $diffSkein); $qubitS = ($qubitCorrFactor / $diffQubit) }
	
	#$hashtablePerWatt
	#""
	#$hashtablePerWattAttenuated
	
	if ( $mode -eq $MODE_MAX_PER_DAY ) {
		$hashtable = $hashtableFactored
	} else {
		$hashtable = $hashtablePerWattAttenuated
	}
	
	$valArraySorted = ($hashtable.GetEnumerator() | Sort-Object Value -descending)
	
	$maxAlgo = $valArraySorted[0].name
	$maxValue = $valArraySorted[0].value
	
	#$newValScrypt  = "{0:f0}" -f $hashtableOriginal.Get_Item($scryptS)
	#$newValGroestl = "{0:f0}" -f $hashtableOriginal.Get_Item($groestlS)
	#$newValSkein   = "{0:f0}" -f $hashtableOriginal.Get_Item($skeinS)
	#$newValQubit   = "{0:f0}" -f $hashtableOriginal.Get_Item($qubitS)
	
	$newVal  = $maxValue
	
	if ( $current ) {
		$prevVal = $hashtable.Get_Item($current)
		
		$greaterThanHys = ( ! $prevVal ) -or ( [decimal]$newVal / [decimal]$prevVal ) -gt $hysteresis
		#$greaterThanMin = ( $timeStint -gt $minTimeNoHysteresis )
		$greaterThanMin = ( (new-timespan $lastStintStart $(Get-Date)).TotalMinutes -gt $minTimeNoHysteresis )
	}
	
	if ( $current -ne $maxAlgo -and ( $greaterThanHys -or $greaterThanMin ) ) {
		
		if ( $current ) {
			$prevAlgo = $current
			
		} else {
			$prevAlgo = $maxAlgo
		}

		$current = $maxAlgo
		
		$prevSwitchtext = $switchtext
	
		switch ($maxAlgo) { 
			$scryptS {
				$switchtext = "> " + $scryptS
				$scriptpath = $scryptBatchFile
				
			} 
			$groestlS {
				$switchtext = "> " + $groestlS
				$scriptpath = $groestlBatchFile
				
			} 
			$skeinS {
				$switchtext = "> " + $skeinS
				$scriptpath = $skeinBatchFile
				
			} 
			$qubitS {
				$switchtext = "> " + $qubitS
				$scriptpath = $qubitBatchFile
			} 
		}
		
		$restart = $True
		$status = "SWITCH"

		$errors = 0
								
	} else {
		$prevAlgo = $current
		$switchtext = "   " + $current
		
		$cpu2 = @(Get-Process -Name $miner* | ForEach-Object {$_.cpu})
		$restart = ! $globalStopped -and ( minerStopped $current $miner $numThreadsPrev $cpu1 $cpu2 )
		
		$cpu1 = $cpu2
			
		if ( $restart ) {
			$switchtext =     "x " + $current
			$status = "FAIL"
			$errors += 1
			
			if ( $errors -ge $maxErrors) {
				$hashtableFactors.set_item( $current, 0 )
				$timeRound -= $sleepSHORT * $ticksPerSec
				$restart = $False
				$errors = 0
				$status = "MAX_FAIL"
			}
		
		} else {
			$switchtext =     ". " + $current
			$status = "OK"
			$errors = 0
		} 
	}
		
	if ( $first ) {
		$lastStintStart = $lastRoundStart = get-date
		$prevStintStart = $prevRoundStart = $lastStintStart
		$globalStart = $lastStintStart
		$prevHashtableCorrected = $hashtableCorrected
	} 
	
	if ( $status -eq "SWITCH" ) {
		$prevStintStart = $lastStintStart
		$lastStintStart = get-date
	} 
	
	$now = get-date
	
	$globalTime 	 = (new-timespan $globalStart $now).ticks
	$globalRoundTime = (new-timespan $prevRoundStart $now).ticks		
	$globalStintTime = (new-timespan $prevStintStart $now).ticks		
	$prevRoundStart = $now
	
	$prevValCorrected = "{0:f0}" -f $prevHashtableCorrected.Get_Item($prevAlgo)
	
	$nextValCorrected = "{0:f0}" -f $hashtableCorrected.Get_Item($current)
	$newValCorrected  = "{0:f0}" -f $hashtableCorrected.Get_Item($prevAlgo)
	
	$wasStopped = $globalStopped
	
	if ( $mode -eq $MODE_MAX_PER_DAY ) {
		$globalStopped = $newValCorrected -lt $minCoins 
		
	} else {
		$averageMinimumCoinsPerWatt = $minCoins / (getAverageHashValues $hashtableWattsAttenuated)
		$globalStopped = $hashtablePerWattAttenuated.get_item($current) -lt $averageMinimumCoinsPerWatt 	
	} 
	
	if ( $globalStopped ) {
		killMiner( "cgminer" )
		killMiner( "sgminer" )
		
		$stopwatch.stop()
		
		if ( ! $status -eq "SWITCH" ) {
			$status = "OK"
		}
		
		$switchtext =     "S " + $current
	}
	
	if ( ( $restart -and ! $globalStopped ) -or ( $wasStopped -and ! $globalStopped ) ) {
		$sleepTime = $sleepLONG
		
		$stopwatch.stop()

		if ( ! $debug ) {	
			killMiner( "cgminer" )
			killMiner( "sgminer" )
		
			$workingDirectory = $scriptpath.substring( 1, $scriptpath.lastindexof("\") )

			Start-Process -FilePath PowerShell.exe  -Verb runAs -ArgumentList "& $scriptpath" -WorkingDirectory $workingDirectory
			$miner = $hashtableMiners.Get_Item($current)
			
			$numThreadsPrev = 0
			while ( ! $numThreadsPrev ) {
				sleep 1
				$numThreadsPrev  =  @(Get-Process -Name $miner*).length
			}
			
			$cpu1 = @( Get-Process -Name $miner* | ForEach-Object {$_.cpu} )	
				
			#write-host "t1 = " + (get-date)	
			sleep $rampUptime
			#write-host "t2 = " + (get-date)
		}
		$stopwatch.start()
		
	} else {
		$sleepTime = $sleepSHORT
	}
	
	if ( ! $prevValCorrected ) {
		$prevValCorrected = $newValCorrected
	}
	
	$avgValCorrected = ( [int]$newValCorrected + [int]$prevValCorrected ) / 2
	
	$prevRoundTicks = $roundTicks
	$elapsedRound = $stopwatch.elapsed
	$roundTicks = $elapsedRound.ticks
	
	[long]$timeRound = ( ( $roundTicks ) - ( $prevRoundTicks ) )
	
	if ( $status -eq "FAIL" ) {
		$timeRound -= ( ( $sleepTime * $ticksPerSec ) / 2 )
	} 
	
	if ( $status -eq "MAX_FAIL" ) {
		$stopwatch.stop()
		
		$timeRound = 0 
		$coinsRound = 0
		$status = "FAIL"
		
		$sleepTime = 0
	
	} else {
		$timeRoundDays = ([timespan]$timeRound).totalDays
		
		$hashtableTime.set_item( $prevAlgo, ( $timeRound + ( $hashtableTime.get_item($prevAlgo) ) ) )
		[decimal]$coinsRound = ( ( [decimal]$avgValCorrected ) * ( [decimal]$timeRoundDays ) )	
	}
	
	$coinsStint = $coinsStint + $coinsRound
	[long]$timeStint = $timeStint + $timeRound
	
	$totalCoinsPrev = $hashtableCoins.get_item($prevAlgo) + $coinsRound
	$hashtableCoins.set_item( $prevAlgo, $totalCoinsPrev )
	
	if ( ( $wasStopped -and ! $first ) -or ( $globalStopped -and $first ) ) {
		$currentWatts = $idleWatts
	
	} else {
		$currentWatts = $hashtableWatts.get_item($prevAlgo)
		if ( $status -eq "FAIL" ) {
			$currentWatts = ( $currentWatts + $idleWatts ) / 2
		} 
	}
	
	[decimal]$wattsRound = ( $currentWatts * ( [decimal]$globalRoundTime ) )
	$wattsStint += $wattsRound
	
	$watts = $watts + $wattsRound 
	
	$totalTime  = (getTotalHashValues $hashtableTime)[1]
	$totalCoins = (getTotalHashValues $hashtableCoins)[1]
	
	if ( ! $previousPrice -or ( $currentPrice -eq $previousPrice ) ) {
		$priceForegroundColor = "White"
	} elseif ( $currentPrice -gt $previousPrice ) {
		$priceForegroundColor = "Green"
	} else {
		$priceForegroundColor = "Red"
	}
	
	if ( $first ) {
		$wattsAvg = $currentWatts
	} else {
		$wattsAvg = $watts / $globalTime
	}
	
	$htmlPTime = 0.0
	
	if ( $status -eq "SWITCH" ) {
		if ( ! $first ) {
			$avgStintWatts = $wattsStint / $globalStintTime
			$htmlPTime += printData "SWITCH" $now $globalStintTime $prevSwitchtext $currentPrice $newValCorrected $spacerColor $coinsStint $avgStintWatts $prevAlgo $globalStopped
		}
		printheader
		
		$coinsStint = 0
		$wattsStint = 0
		$timeStint  = 0
		
		$status = "OK"
	}
	
	$htmlPTime += printData $status $now $globalTime $switchtext $currentPrice $nextValCorrected $spacerColor $totalCoins $wattsAvg $current $globalStopped
	
	$first = 0
	
	#$procTime = $httpTime + $htmlPTime
	
	if ( $htmlPTime -lt $sleepTime ) {
		sleep ( $sleepTime - $htmlPTime )
	} 
	
	loadConfig ( $skeinFactor ) 		
	
	#else {
	#	sleep ( $sleepTime - $procTime )
	#}
}
