let isMouseDown = false;
let startHour = null;
let startEmployeeId = null;
let selectedShifts = [];

$(document).ready(function(){
    // We can parse any existing scheduledShifts from the server to a JS array if needed.
    // For demonstration, we’ll just build from scratch.

    // Mousedown
    $('.sched-cell').on('mousedown', function(e){
        e.preventDefault();
        isMouseDown = true;
        startHour = $(this).data('hour');
        startEmployeeId = $(this).closest('tr').data('employee-id');
        // Clear any previous highlight if needed.
        // ...
    });

    // Mouseover (drag)
    $('.sched-cell').on('mouseover', function(e){
        if(isMouseDown){
            // We can highlight the range in real-time.
            const currentHour = $(this).data('hour');
            const currentEmpId = $(this).closest('tr').data('employee-id');
            if(currentEmpId === startEmployeeId){
                // highlight from startHour -> currentHour
                // ...
            }
        }
    });

    // Mouseup
    $(document).on('mouseup', function(e){
        if(isMouseDown){
            isMouseDown = false;
            // We finalize the shift
            // End hour:
            let endCell = $(e.target).closest('.sched-cell');
            if(endCell.length > 0){
                let endHour = endCell.data('hour');
                let endEmployeeId = endCell.closest('tr').data('employee-id');
                if(endEmployeeId === startEmployeeId){
                    let minHour = Math.min(startHour, endHour);
                    let maxHour = Math.max(startHour, endHour) + 1; // +1 so it’s exclusive end
                    // Record shift in our array (remove any existing overlapping for that employee)
                    selectedShifts = selectedShifts.filter(s => s.employee_id !== startEmployeeId);
                    selectedShifts.push({
                        employee_id: startEmployeeId,
                        start: minHour,
                        end: maxHour
                    });
                }
            }
        }
    });
});

// Called by “Save Schedule” button
function saveSchedule(){
    // Put array into hidden field as JSON
    $('#new_shifts').val(JSON.stringify(selectedShifts));
    // Submit the form
    $('form')[0].submit();
}
