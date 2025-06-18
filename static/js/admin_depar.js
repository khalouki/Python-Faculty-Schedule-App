function openEditModal(id, name, description) {
    document.getElementById('edit_department_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_description').value = description;
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