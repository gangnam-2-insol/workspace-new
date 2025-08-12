Param(
  [switch]$DryRun
)

$paths = @(
  'admin/backend/.venv',
  'admin/backend/data/uploads',
  'admin/backend/data/images',
  'admin/backend/data/results',
  'admin/backend/vector_db',
  'vector_db',
  'data/uploads',
  'data/images',
  'data/results'
)

Write-Host "Cleanup targets:" -ForegroundColor Cyan
$paths | ForEach-Object { Write-Host " - $_" }

foreach ($p in $paths) {
  if (Test-Path $p) {
    if ($DryRun) {
      Write-Host "[DRY RUN] Would remove: $p" -ForegroundColor Yellow
    } else {
      try {
        Remove-Item -Recurse -Force -LiteralPath $p -ErrorAction Stop
        Write-Host "Removed: $p" -ForegroundColor Green
      } catch {
        Write-Host "Failed to remove ${p}: $($_.Exception.Message)" -ForegroundColor Red
      }
    }
  }
}

Write-Host "Done." -ForegroundColor Cyan

