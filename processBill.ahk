; ==================================================
; processBill.ahk
; Process line items inside a bill
; ==================================================

ProcessBill()
{
    global StopProcessing
    sleep 500
    Debug("ProcessBill start")

    ; Move to Customer Job dropdown
    Click 1505, 724 
    Sleep 200
    Loop 2
    {
        if (StopProcessing)
            return

        Send {Tab}
        Sleep 80
    }

    Sleep 500

    ; Loop through line items
    Loop
    {
        if (StopProcessing)
            return

        Debug("Processing line item")

        ; Open dropdown
        Send !{Down}
        Sleep 400

        ; Move to top
        Loop 6
        {
            Send {Up}
            Sleep 80
        }

        Sleep 200

        ; Move off "Create New"
        Send {Down}
        Sleep 150

        ; Search entries
        Loop 6
        {
            if (StopProcessing)
                return

            Send {Enter}
            Sleep 300

            clipboard := ""
            Send ^c
            ClipWait, .3

            Debug("Clipboard: " clipboard)

            if InStr(clipboard, "20961 Skyler")
            {
                Debug("Matched Skyler")
                break
            }

            Send !{Down}
            Sleep 200

            Send {Down}
            Sleep 150
        }

        ; Move to next line
        Send {Tab 8}
        Sleep 400

        ; Detect end
        clipboard := ""
        Send ^c
        ClipWait, 1

        if (clipboard = "")
        {
            Debug("End of lines")
            break
        }
    }

    Debug("Saving bill")

    ; =========================================
    ; Close and Save Bill
    ; =========================================
    Send !a
    Sleep 300

    ; =========================================
    ; Only press Enter if dialog appears
    ; =========================================
    WinWaitActive, Recording Transaction,, 1

    if (!ErrorLevel)
    {
        Debug("Recording Transaction dialog detected")
        Send {Enter}
        Sleep 600
    }
    else
    {
        Debug("No Recording dialog")
    }

    Debug("ProcessBill finished")
}