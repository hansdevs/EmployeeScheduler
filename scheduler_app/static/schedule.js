let isMouseDown = false;
let startHour = null;
let startEmployeeId = null;
let selectedShifts = []; 

// For multi-day: we can just hard-code day=0 for now
let currentDay = 0;

$(document).ready(function(){

  // Drag logic
  $('.sched-cell').on('mousedown', function(e){
    e.preventDefault();
    isMouseDown = true;
    startHour = $(this).data('hour');
    startEmployeeId = $(this).closest('tr').data('employee-id');
  });

  $('.sched-cell').on('mouseover', function(){
    if(isMouseDown) {
      const curHour = $(this).data('hour');
      const curEmpId = $(this).closest('tr').data('employee-id');
      if(curEmpId === startEmployeeId) {
        $(this).addClass('drag-over');
      }
    }
  }).on('mouseleave', function(){
    $(this).removeClass('drag-over');
  });

  $(document).on('mouseup', function(e){
    if(!isMouseDown) return;
    isMouseDown = false;

    const endCell = $(e.target).closest('.sched-cell');
    if(endCell.length) {
      const endHour = endCell.data('hour');
      const endEmpId = endCell.closest('tr').data('employee-id');
      if(endEmpId === startEmployeeId) {
        let minH = Math.min(startHour, endHour);
        let maxH = Math.max(startHour, endHour) + 1; // exclusive end

        // remove old shift for this employee on this day
        selectedShifts = selectedShifts.filter(s =>
          !(s.employee_id === startEmployeeId && s.day === currentDay)
        );

        // create new shift
        selectedShifts.push({
          employee_id: startEmployeeId,
          start: minH,
          end: maxH,
          day: currentDay
        });

        // Clear old visuals for that employee in the table
        const row = $('tr[data-employee-id="'+startEmployeeId+'"]');
        row.find('.scheduled-block').remove();

        // figure out that employee's color from the server data
        // we have no direct object here, so let's store them in a data attr or do an AJAX fetch
        // for now, parse from the row’s data- attributes or fallback to "block-blue"
        const colorClass = getEmployeeColor(startEmployeeId) || "block-blue";

        for(let h = minH; h < maxH; h++){
          const cell = row.find('.sched-cell[data-hour="'+h+'"]');
          cell.empty().append(`
            <div class="scheduled-block ${colorClass}">Scheduled</div>
          `);
        }
      }
    }
    // remove highlight
    $('.sched-cell').removeClass('drag-over');
  });

  // Hide cleaning employees example
  $('#hideCleaningSwitch').on('change', function(){
    if($(this).is(':checked')){
      $('tr[data-emp-type="Cleaning"]').hide();
    } else {
      $('tr[data-emp-type="Cleaning"]').show();
    }
  });
});

function getEmployeeColor(empId){

  let colorClass = $('tr[data-employee-id="'+empId+'"]').data('employeeColor');
  return colorClass;
}

// Save button
function saveSchedule(){
  $('#new_shifts').val(JSON.stringify(selectedShifts));
  $('form')[0].submit();
}
