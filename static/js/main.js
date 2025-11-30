// Main JavaScript for Digital Learning Library

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Scroll to top button
    const scrollTopBtn = $('<button id="scrollTopBtn" title="Go to top"><i class="fas fa-arrow-up"></i></button>');
    $('body').append(scrollTopBtn);

    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#scrollTopBtn').fadeIn();
        } else {
            $('#scrollTopBtn').fadeOut();
        }
    });

    $('#scrollTopBtn').click(function() {
        $('html, body').animate({ scrollTop: 0 }, 600);
        return false;
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('[data-confirm]').on('click', function(e) {
        const message = $(this).data('confirm');
        if (!confirm(message)) {
            e.preventDefault();
            return false;
        }
    });

    // Form validation feedback
    $('form').on('submit', function() {
        const form = $(this);
        if (form[0].checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.addClass('was-validated');
    });

    // Search autocomplete
    $('#searchInput').on('input', debounce(function() {
        const query = $(this).val();
        if (query.length > 2) {
            $.ajax({
                url: '/api/search',
                data: { q: query, limit: 5 },
                success: function(data) {
                    displaySearchSuggestions(data.results);
                }
            });
        }
    }, 300));

    // Loading spinner
    $(document).ajaxStart(function() {
        showLoading();
    }).ajaxStop(function() {
        hideLoading();
    });

    // Book rating
    $('.rating-star').on('click', function() {
        const rating = $(this).data('rating');
        $('#rating-input').val(rating);
        updateStarDisplay(rating);
    });

    // Image preview before upload
    $('input[type="file"]').on('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#image-preview').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        }
    });

    // Copy to clipboard
    $('.copy-btn').on('click', function() {
        const text = $(this).data('copy');
        copyToClipboard(text);
        showToast('Copied to clipboard!');
    });

    // Infinite scroll for book listings
    let page = 1;
    let loading = false;
    
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
            if (!loading && $('#load-more').length) {
                loading = true;
                loadMoreBooks();
            }
        }
    });
});

// Utility Functions

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function showLoading() {
    if ($('#loading-overlay').length === 0) {
        const overlay = $('<div id="loading-overlay" class="spinner-overlay">' +
            '<div class="spinner-border text-primary" role="status">' +
            '<span class="visually-hidden">Loading...</span>' +
            '</div></div>');
        $('body').append(overlay);
    }
    $('#loading-overlay').fadeIn();
}

function hideLoading() {
    $('#loading-overlay').fadeOut();
}

function showToast(message, type = 'success') {
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    setTimeout(() => toast.remove(), 5000);
}

function copyToClipboard(text) {
    const tempInput = $('<textarea>');
    $('body').append(tempInput);
    tempInput.val(text).select();
    document.execCommand('copy');
    tempInput.remove();
}

function displaySearchSuggestions(results) {
    const suggestionsList = $('#search-suggestions');
    suggestionsList.empty();
    
    if (results.length === 0) {
        suggestionsList.hide();
        return;
    }
    
    results.forEach(book => {
        const item = $(`
            <a href="/books/${book.id}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${book.title}</h6>
                </div>
                <small class="text-muted">${book.author}</small>
            </a>
        `);
        suggestionsList.append(item);
    });
    
    suggestionsList.show();
}

function updateStarDisplay(rating) {
    $('.rating-star').each(function() {
        const starRating = $(this).data('rating');
        if (starRating <= rating) {
            $(this).removeClass('far').addClass('fas');
        } else {
            $(this).removeClass('fas').addClass('far');
        }
    });
}

function loadMoreBooks() {
    page++;
    const url = window.location.pathname + '?page=' + page;
    
    $.get(url, function(data) {
        const books = $(data).find('.book-card');
        $('#books-container').append(books);
        loading = false;
        
        if (books.length === 0) {
            $('#load-more').remove();
        }
    });
}

// AJAX form submission
function submitAjaxForm(form, successCallback) {
    const formData = new FormData(form[0]);
    
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                showToast(response.message || 'Operation successful!', 'success');
                if (successCallback) successCallback(response);
            } else {
                showToast(response.error || 'Operation failed!', 'danger');
            }
        },
        error: function(xhr) {
            showToast('An error occurred. Please try again.', 'danger');
        }
    });
}

// Book borrowing
function borrowBook(bookId) {
    if (!confirm('Are you sure you want to borrow this book?')) {
        return;
    }
    
    $.post(`/books/${bookId}/borrow`, function(response) {
        if (response.success) {
            showToast('Book borrowed successfully!', 'success');
            setTimeout(() => window.location.href = '/user/dashboard', 1500);
        } else {
            showToast(response.error || 'Failed to borrow book', 'danger');
        }
    }).fail(function() {
        showToast('An error occurred', 'danger');
    });
}

// Book reservation
function reserveBook(bookId) {
    $.post(`/books/${bookId}/reserve`, function(response) {
        if (response.success) {
            showToast('Book reserved successfully!', 'success');
        } else {
            showToast(response.error || 'Failed to reserve book', 'danger');
        }
    });
}

// Export functions for global access
window.libraryApp = {
    borrowBook,
    reserveBook,
    showToast,
    showLoading,
    hideLoading,
    submitAjaxForm
};

// Service Worker Registration (for PWA support)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/sw.js')
        .then(reg => console.log('Service Worker registered'))
        .catch(err => console.log('Service Worker registration failed'));
}
