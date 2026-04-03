; ==================================================
; setExemptInItems.ahk
; ==================================================

running := false
StopProcessing := false

CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

RowHeight := 26


; =========================================
; Helper: Tab Multiple Times
; =========================================
TabLoop(count)
{
    Loop %count%
    {
        Send {Tab}
        Sleep 80
    }
}


; =========================================
; Start Processing
; =========================================
F2::

running := true
StopProcessing := false

Loop
{
    if (!running || StopProcessing)
        break

    ; Double click item
    Click
    Sleep 100
    Click
    Sleep 900

    ; Give QuickBooks time to draw UI
    Sleep 200

    ; =========================================
    ; Check UNCHECKED first
    ; =========================================
    ImageSearch, fx, fy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 subitem_unchecked.png

    if (ErrorLevel = 0)
    {
        ; Not subitem — move to OK
        TabLoop(7)

        Send {Enter}
        Sleep 600

        MouseMove, 0, RowHeight, 0, R
        Sleep 300

        continue
    }

    ; =========================================
    ; Check CHECKED
    ; =========================================
    ImageSearch, fx, fy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 subitem_checked.png

    if (ErrorLevel = 0)
    {
        ; Process item
        TabLoop(6)

        Send e
        Sleep 200

        Send {Enter}
        Sleep 300

        TabLoop(5)

        Send e
        Sleep 200

        Send {Enter}
        Sleep 300

        ; Already positioned at OK
        Send {Enter}
        Sleep 600

        MouseMove, 0, RowHeight, 0, R
        Sleep 300

        continue
    }

    ; =========================================
    ; Fallback
    ; =========================================
    Send {Esc}
    Sleep 300

    MouseMove, 0, RowHeight, 0, R
    Sleep 300
}

return


; =========================================
; ESC - Stop Immediately
; =========================================
Esc::
running := false
StopProcessing := true
return