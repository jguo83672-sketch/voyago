document.addEventListener('DOMContentLoaded', function() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('hide');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    });

    const searchForms = document.querySelectorAll('form[action*="search"]');
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = this.querySelector('input[type="search"], input[name="q"]');
            if (input && input.value.trim() === '') {
                e.preventDefault();
                input.classList.add('is-invalid');
            }
        });

        const input = form.querySelector('input[type="search"], input[name="q"]');
        if (input) {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        }
    });

    // 导航栏滚动效果
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 轮播自动播放设置
    const heroCarousel = document.getElementById('heroCarousel');
    if (heroCarousel) {
        const carousel = new bootstrap.Carousel(heroCarousel, {
            interval: 5000,
            wrap: true,
            keyboard: true
        });
    }
});

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatNumber(num) {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
    }
    return num.toString();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('已复制到剪贴板');
    }).catch(err => {
        console.error('复制失败:', err);
    });
}

function confirmDelete(message) {
    return confirm(message || '确定要删除吗？');
}

function toggleLike(element) {
    element.classList.toggle('liked');
    const icon = element.querySelector('i');
    if (element.classList.contains('liked')) {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
    } else {
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
    }
}

document.querySelectorAll('.favorite-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const type = this.dataset.type;
        const id = this.dataset.id;
        
        fetch(`/toggle-favorite/${type}/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.favorited) {
                    this.classList.add('active');
                    this.innerHTML = '<i class="bi bi-heart-fill"></i> 已收藏';
                } else {
                    this.classList.remove('active');
                    this.innerHTML = '<i class="bi bi-heart"></i> 收藏';
                }
            })
            .catch(error => console.error('操作失败:', error));
    });
});

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

window.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scrollToTop');
    if (scrollBtn) {
        if (window.scrollY > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    }
});
