; ==================================================
; processVendorList.ahk
;
; PURPOSE:
; Top level vendor processing
; Beta 1.1
; ==================================================

#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

#Include processVendor.ahk

; Global variables
StopProcessing := false
VendorStep := 30
BillX := 1631
BillY := 778


; =========================================
; F1 - Process Vendor List
; =========================================
F1::
global StopProcessing, VendorStep, BillX, BillY
StopProcessing := false
VendorStep := 31
BillX := 1631
BillY := 778

StopProcessing := false

; Capture starting vendor position
MouseGetPos, startX, startY
currentY := startY

Debug("Starting vendor list processing")

Loop
{
    ; Stop if ESC pressed
    if (StopProcessing)
    {
        Debug("Stopped by user")
        break
    }

    ; Click vendor
  
    MouseClick, left, %startX%, %currentY%

    Sleep 1000

    Debug("Clicked vendor at Y: " currentY)

    ; Click first bill

    MouseClick, left, %BillX%, %BillY%
    Sleep 1000

    ; Process vendor
    ProcessVendor()

    ; Move to next vendor
    currentY += VendorStep

    Debug("Moving to next vendor")
    Sleep 1000
}

Debug("Finished vendor list")

Return