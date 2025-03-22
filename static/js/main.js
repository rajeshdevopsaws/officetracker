document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/api/events',
        eventDidMount: function(info) {
            // Add the type class to the event element
            info.el.classList.add(info.event.extendedProps.type);
        },
        eventClick: function(info) {
            showEventModal(info.event);
        }
    });
    
    calendar.render();

    $('#eventForm').on('submit', function(e) {
        e.preventDefault();
        
        const data = {
            date: $('#date').val(),
            type: $('#type').val()
        };

        $.ajax({
            url: '/api/events',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                calendar.refetchEvents();
                $('#eventForm')[0].reset();
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Failed to add event. Please try again.');
            }
        });
    });

    // Event Modal Handlers
    function showEventModal(event) {
        const modal = $('#eventModal');
        modal.find('#editDate').val(event.startStr);
        modal.find('#editType').val(event.extendedProps.type);
        modal.find('#eventId').val(event.id);
        modal.modal('show');
    }

    $('#updateEventForm').on('submit', function(e) {
        e.preventDefault();
        const eventId = $('#eventId').val();
        const data = {
            date: $('#editDate').val(),
            type: $('#editType').val()
        };

        $.ajax({
            url: `/api/events/${eventId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                calendar.refetchEvents();
                $('#eventModal').modal('hide');
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Failed to update event. Please try again.');
            }
        });
    });

    $('#deleteEvent').on('click', function() {
        if (confirm('Are you sure you want to delete this event?')) {
            const eventId = $('#eventId').val();
            
            $.ajax({
                url: `/api/events/${eventId}`,
                method: 'DELETE',
                success: function(response) {
                    calendar.refetchEvents();
                    $('#eventModal').modal('hide');
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                    alert('Failed to delete event. Please try again.');
                }
            });
        }
    });

    // Export form handler
    $('#exportForm').on('submit', function(e) {
        e.preventDefault();
        
        const monthInput = $('#exportMonth').val(); // Format: "YYYY-MM"
        const [year, month] = monthInput.split('-');
        
        // Create the download URL
        const downloadUrl = `/api/export/${year}/${month}`;
        
        // Trigger the download
        window.location.href = downloadUrl;
    });
}); 