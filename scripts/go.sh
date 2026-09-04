#!/bin/bash
# Stage, de-CRLF, and run the fleet. Everything is in files so no quoting
# crosses the PowerShell -> SSH -> cmd -> wsl -> bash boundary.
mkdir -p $HOME/bin $HOME/stl
cp /mnt/c/Temp/fleet/*.sh $HOME/bin/
cp /mnt/c/Temp/fleet/*.stl $HOME/stl/ 2>/dev/null
cp /mnt/c/Temp/fleet/manifest.txt $HOME/
sed -i 's/\r$//' $HOME/bin/*.sh $HOME/manifest.txt
chmod +x $HOME/bin/*.sh
rm -f $HOME/aero/fleet_results.tsv
echo "--- manifest ---"; cat -A $HOME/manifest.txt | head -5
bash $HOME/bin/fleet.sh $HOME/manifest.txt
