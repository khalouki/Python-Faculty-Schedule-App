
// Variable globale pour suivre le formulaire courant
let currentForm = null;

function openEditModal(id, username, email, first_name, last_name, type) {
    // Réinitialiser le formulaire courant
    currentForm = null;
    
    // Remplir les champs du modal
    document.getElementById('edit_teacher_id').value = id;
    document.getElementById('edit_username').value = username;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit_first_name').value = first_name;
    document.getElementById('edit_last_name').value = last_name;
    document.getElementById('edit_type').value = type;
    document.getElementById('edit_password').value = '';

    // Centrer et afficher le modal
    const modal = document.getElementById('editModal');
    const modalContent = modal.querySelector('div');
    
    const viewportHeight = window.innerHeight;
    const scrollY = window.scrollY;
    
    modalContent.style.position = 'fixed';
    modalContent.style.top = `${scrollY + viewportHeight / 2}px`;
    modalContent.style.left = '50%';
    modalContent.style.transform = 'translate(-50%, -50%)';
    
    // Afficher le modal et bloquer le défilement
    modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

function confirmEmail() {
    document.getElementById('send_email').value = 'true';
    document.getElementById('emailModal').classList.add('hidden');
    if (currentForm) {
        currentForm.submit();
    }
}

function cancelEmail() {
    document.getElementById('send_email').value = 'false';
    document.getElementById('emailModal').classList.add('hidden');
    if (currentForm) {
        currentForm.submit();
    }
}

// Gestion de la soumission des formulaires
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[method="POST"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.querySelector('input[name="_method"][value="POST"], input[name="_method"][value="PUT"]')) {
                e.preventDefault();
                currentForm = this;
                document.getElementById('emailModal').classList.remove('hidden');
            }
        });
    });
});
