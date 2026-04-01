#Include processVendor.ahk
#Include processBill.ahk

; ==================================================
; processVendorList.ahk
; Top Level Controller
; ==================================================

CoordMode, Mouse, Screen


; --------------------------------------------------
; F1 - Process all vendors
; --------------------------------------------------
F1::

; Click first vendor (Amazon)
Click 740, 347
Sleep 500

; Loop vendors
Loop 36
{
    Send {Enter}
    Sleep 2000

    ProcessVendor()

    Sleep 800
    Send {Down}
    Sleep 300
}

Return


; --------------------------------------------------
; F2 - Process current vendor
; --------------------------------------------------
F2::
ProcessVendor()
Return


; --------------------------------------------------
; F3 - Process highlighted bill
; --------------------------------------------------
F3::

; Open highlighted bill
Send {Enter}
Sleep 2000

; Process the bill
ProcessBill()

Return


; --------------------------------------------------
; Emergency stop
; --------------------------------------------------
Esc::ExitApp