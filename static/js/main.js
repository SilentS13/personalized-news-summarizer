// Main JavaScript Functionality

// Function to highlight interest topics in the summary
function highlightInterests() {
    const interests = document.querySelectorAll('.interest-highlight');
    
    interests.forEach(element => {
        // Add animation effect when highlighting
        element.classList.add('fade-in');
        
        // Ensure proper styling
        if (!element.style.backgroundColor) {
            element.style.backgroundColor = 'rgba(var(--bs-info-rgb), 0.2)';
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Apply interest highlighting
    highlightInterests();
    
    // Add smooth fade-in for page content
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize dismissible alerts
    const alertElements = document.querySelectorAll('.alert-dismissible');
    alertElements.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Auto close after 5 seconds
    });
});