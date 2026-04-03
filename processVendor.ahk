; ==================================================
; processVendor.ahk
;
; PURPOSE:
; Process bills starting from currently selected bill
;
; CONTROLS:
; F2 = Process all bills
; F3 = Process one bill
; ESC = Stop immediately
;
; METHOD:
; - Capture selected bill coordinates
; - Process bill
; - Move down to next bill
; - Only re-click if focus lost
; Beta 1.1
; ==================================================

#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

#Include processBill.ahk

global StopProcessing := false


; =========================================
; Debug function
; =========================================
Debug(msg)
{
    FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
    FileAppend, %timestamp% - %msg%`n, QuickBooks_Debug.log
}


; =========================================
; F2 - Process All Bills
; =========================================
F2::
StopProcessing := false
Debug("F2 pressed - starting ProcessVendor")
ProcessVendor()
Return


; =========================================
; F3 - Process One Bill
; =========================================
F3::
StopProcessing := false
Debug("F3 pressed - single bill")
ProcessSingleBill()
Return


; =========================================
; ESC - Stop Immediately
; =========================================
Esc::
StopProcessing := true
Debug("ESC pressed - stopping")
Return


; =========================================
; Process All Bills
; =========================================
ProcessVendor()
{
    global StopProcessing

    Debug("ProcessVendor start")

    ; Capture initial mouse position
    MouseGetPos, xpos, ypos
    Debug("Initial position captured: " xpos "," ypos)

    ; Click once to ensure focus
    MouseClick, left, %xpos%, %ypos%
    Sleep 800

    Loop
    {
        ; Stop if ESC pressed
        if (StopProcessing)
        {
            Debug("StopProcessing detected")
            break
        }

        ; Open highlighted bill
        Debug("Opening bill")
        Send {Enter}
        Sleep 1500

        ; Confirm bill opened
        WinGetTitle, title, A
        Debug("Window title: " title)

        if !(InStr(title, "Bill") || InStr(title, "Enter Bills"))
        {
            Debug("No bill opened - exiting loop")
            break
        }

        ; Process bill
        Debug("Calling ProcessBill")
        ProcessBill()

        ; Stop if ESC pressed
        if (StopProcessing)
        {
            Debug("StopProcessing after ProcessBill")
            break
        }

        Sleep 800

        ; Move to next bill
        Debug("Moving to next bill")
        Send {Down}
        Sleep 600

        ; Small pause for QuickBooks UI stability
        Sleep 200
    }

    Debug("ProcessVendor finished")
}


; =========================================
; Process Single Bill
; =========================================
ProcessSingleBill()
{
    Debug("ProcessSingleBill start")

    Send {Enter}
    Sleep 1500

    WinGetTitle, title, A
    Debug("Window title: " title)

    if !(InStr(title, "Bill") || InStr(title, "Enter Bills"))
        return

    ProcessBill()

    Debug("ProcessSingleBill finished")
}

TabLoop(x)
{
    Loop %x%
    {
        Send {Tab}
        Sleep 100
    }
}