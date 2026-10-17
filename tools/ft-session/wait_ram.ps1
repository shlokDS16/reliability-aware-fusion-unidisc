# Exit when free physical memory >= $args[0] GB (default 8), or after $args[1] minutes (default 60). Prints the free GB.
param([double]$need = 8, [int]$maxmin = 60)
$t0 = Get-Date
while ($true) {
  $free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
  if ($free -ge $need -or ((Get-Date) - $t0).TotalMinutes -ge $maxmin) { "free_gb={0:N1} minutes={1:N0}" -f $free, ((Get-Date) - $t0).TotalMinutes; break }
  Start-Sleep -Seconds 30
}
