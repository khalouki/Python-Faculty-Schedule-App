function openEditModal(id, name, department_id, duration, year) {
    document.getElementById('edit_program_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_department').value = department_id;
    document.getElementById('edit_duration').value = duration;
    document.getElementById('edit_year').value = year;
    document.getElementById('editModal').classList.remove('hidden');

    // Get modal and content
    const modal = document.getElementById('editModal');
    const modalContent = modal.querySelector('div');

    // Center modal in current viewport
    const viewportHeight = window.innerHeight;
    const scrollY = window.scrollY;
    modalContent.style.position = 'fixed';
    modalContent.style.top = `${scrollY + viewportHeight / 2}px`;
    modalContent.style.left = '50%';
    modalContent.style.transform = 'translate(-50%, -50%)';

    // Show modal and block scroll
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');

}