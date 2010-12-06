#!/usr/bin/ksh
#    This file is part of burnstation2.

#    burnstation2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    burnstation2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with burnstation2.  If not, see <http://www.gnu.org/licenses/>.

# (C) 2010 by Stefan Marsiske, <stefan.marsiske@gmail.com>

# depends on pmount, dbus-monitor

LABEL=burnstation
MOUNTDIR=/media/$LABEL
DEVICE=/tmp/mounted-usb

#TODO improvement, do not mount the biggest but the partition with the most free space

rm $DEVICE

function add {
    read object
    object="${object##*/}"
    object="${object%\"}"
    [[ ${#object} -eq 3 ]] && {
        grep "${object}[0-9]" /proc/partitions | sed 's/  */ /g' | cut -d' ' -f4,5 | sort -rn | cut -d' ' -f2 | while read part; do
        echo "trying $part"
        pmount -s -t vfat -p /dev/null "/dev/$part" "$LABEL" 2>/dev/null && {
            echo "${part}" >"$DEVICE"
            echo ok
            return
        }
       done
    }
}

function remove {
    read object
    object="${object##*/}"
    object="${object%\"}"
    [[ ${#object} -eq "$(cat $DEVICE 2>/dev/null)" ]] && {
        rm "$DEVICE"
    }
}

dbus-monitor --system "type='signal',interface='org.freedesktop.UDisks'" |
  while read signal; do
     case "${signal}" in
         *member=DeviceAdded) add;;
         *member=DeviceRemoved) remove;;
     esac
done
