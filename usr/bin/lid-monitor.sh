#!/usr/bin/env bash

set -u

LID_STATE_FILE=""

for f in /proc/acpi/button/lid/*/state; do
    if [[ -r "$f" ]]; then
        LID_STATE_FILE="$f"
        break
    fi
done

if [[ -z "$LID_STATE_FILE" ]]; then
    echo "Could not find laptop lid state."
    exit 1
fi

external_connected() {
    for status_file in /sys/class/drm/*-HDMI-A-1/status; do
        [[ -r "$status_file" ]] || continue

        if [[ "$(cat "$status_file")" == "connected" ]]; then
            return 0
        fi
    done

    return 1
}

last_state=""
last_external_state=""

while true; do
    state="$(awk '{print $2}' "$LID_STATE_FILE")"

    if external_connected; then
        external_state="connected"
    else
        external_state="disconnected"
    fi

    # A disconnect can happen while the lid remains closed, so handle it
    # independently of lid-state changes.  Restore both internal displays in
    # that case rather than leaving the laptop without an active display.
    if [[ "$last_external_state" == "connected" && "$external_state" == "disconnected" ]]; then
        echo "External monitor disconnected; enabling internal displays"

        kscreen-doctor \
            output.eDP-1.enable \
            output.eDP-2.enable
    fi

    if [[ "$state" != "$last_state" ]]; then
        if [[ "$external_state" == "connected" ]]; then
            case "$state" in
                closed)
                    echo "Lid closed + external monitor connected"
                    echo "Disabling internal displays"

                    kscreen-doctor \
                        output.eDP-1.disable \
                        output.eDP-2.disable \
                        output.HDMI-A-1.enable
                    ;;

                open)
                    echo "Lid opened + external monitor connected"
                    echo "Enabling internal displays"

                    kscreen-doctor \
                        output.eDP-1.enable \
                        output.eDP-2.enable
                    ;;
            esac
        else
            echo "No external monitor connected; leaving displays unchanged"
        fi

        last_state="$state"
    fi

    last_external_state="$external_state"

    sleep 1
done
