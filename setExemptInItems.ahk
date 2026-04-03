; ==================================================
; setExemptInItems.ahk
;
; PURPOSE:
; Set Exempt values in item dialog repeatedly
;
; CONTROLS:
; F2 = Start
; ESC = Stop
; ==================================================

running := false
StopProcessing := false

RowHeight := 30


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

    ; First Exempt
    TabLoop(6)

    Send e
    Sleep 200

    Send {Enter}
    Sleep 300

    ; Second Exempt
    TabLoop(5)

    Send e
    Sleep 200

    Send {Enter}
    Sleep 300

    ; OK button
    Send {Enter}
    Sleep 600

    ; Move to next item
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