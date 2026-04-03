; ==================================================
; processBill.ahk
; Process line items inside a bill
; Beta 1.1
; ==================================================

ProcessBill()
{
    global StopProcessing
    sleep 500
    Debug("ProcessBill start")

    sleep 100
    Loop 7
    {
        if (StopProcessing)
            return

        Send {Tab}
        Sleep 100
    }
    Sleep 200

    ;move to dropdown
    ; Copy dropdown contents
clipboard := ""
Send ^c
ClipWait, 0.5
dropdownValue := clipboard
; msgBox drop down value is %dropdownValue%

processItemDropdown()

  
    Loop 6
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
        Send {Tab 2}
        Sleep 400


        ; Detect end
        clipboard := ""
        Send ^c
        ClipWait, 1

        ;see if the itemlist is blank
        if (clipboard = "")
        {
            Debug("End of lines")
            break
        }
                processItemDropdown()
        send {Tab 6}
        sleep 500
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

processItemDropdown()
{

; Open dropdown
Send !{Down}
Sleep 1000

; Move down one
Send {Down}
Sleep 1000


send {enter}

Send !{Down}
; opendrop down
Sleep 1000
; Move up one
Send {Up}
Sleep 1000

; select the entry
send {enter}
sleep 1000
}