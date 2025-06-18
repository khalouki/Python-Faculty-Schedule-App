// Define the base URL for the export endpoint with a fallback
let baseUrl = "{{ url_for('admin.export_schedule_pdf') }}";
if (baseUrl.includes("url_for")) {
    console.warn("Jinja2 failed to evaluate url_for, using fallback URL");
    baseUrl = "/admin/export/schedule/pdf";
}
console.log("Export Base URL:", baseUrl);

function updateExportLink() {
    const programId = document.getElementById('filter_program').value;
    const year = document.getElementById('filter_year').value;
    const url = new URL(baseUrl, window.location.origin);
    
    // Only add parameters if they have values
    if (programId) url.searchParams.set('program_id', programId);
    if (year) url.searchParams.set('year', year);
    
    const exportLink = document.getElementById('export_pdf_link');
    exportLink.href = url.toString();
    
    // Disable the export button if no filters are selected
    exportLink.classList.toggle('opacity-50', !programId || !year);
    exportLink.classList.toggle('pointer-events-none', !programId || !year);
    console.log("Export link updated to:", url.toString());
}

// Initialize the export link on page load
document.addEventListener('DOMContentLoaded', function() {
    updateExportLink();
    
    // Add event listeners for filter changes
    document.getElementById('filter_program').addEventListener('change', updateExportLink);
    document.getElementById('filter_year').addEventListener('change', updateExportLink);
    
    // Update on form submission
    document.getElementById('filterForm').addEventListener('submit', function() {
        updateExportLink();
    });
});

// Modal functions
function openScheduleModal(id, program_id, year, course_id, teacher_id, group_id, room_id, day, start_time, end_time) {
    console.log('Opening modal with:', { id, program_id, year, course_id, teacher_id, group_id, room_id, day, start_time, end_time });
    document.getElementById('edit_schedule_id').value = id;
    document.getElementById('edit_program').value = program_id;
    document.getElementById('edit_year').value = year;
    document.getElementById('edit_course').value = course_id;
    document.getElementById('edit_teacher').value = teacher_id;
    document.getElementById('edit_group').value = group_id === 'null' ? 'all' : group_id;
    document.getElementById('edit_room').value = room_id;
    document.getElementById('edit_day').value = day;
    document.getElementById('edit_start_time').value = start_time;
    document.getElementById('edit_end_time').value = end_time;

    const modal = document.getElementById('editScheduleModal');
    modal.classList.remove('hidden');
    modal.scrollIntoView({ behavior: 'smooth', block: 'center' });
    document.body.classList.add('overflow-hidden');
}

function closeScheduleModal() {
    document.getElementById('editScheduleModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}
