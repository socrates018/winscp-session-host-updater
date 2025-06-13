# winscp-session-gateway-updater

I created this script because I frequently use FTP to transfer files between my Android phone and Windows computer. In recent versions of Android, every time the hotspot function is enabled, the AP's network subnet—and thus the gateway address—are different. To avoid manually changing the host in WinSCP every time, I created this script.

For now, this script needs the `.ini` file of WinSCP, which is located in AppData/Roaming. By default, WinSCP uses the Windows registry to save all its configuration (and sessions). In Settings > Storage, WinSCP must be configured to use the automatic `.ini` file option for the script to work. (Warning: you will need to re-enter saved session passwords.)