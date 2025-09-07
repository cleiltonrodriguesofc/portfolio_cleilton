document.addEventListener("DOMContentLoaded", function() {
    const toggleSidebarBtn = document.querySelector(".toggle-sidebar");
    const sidebar = document.querySelector(".sidebar");
    const content = document.querySelector(".content");
    const sidebarOverlay = document.createElement("div");
    sidebarOverlay.classList.add("sidebar-overlay");
    document.body.appendChild(sidebarOverlay);

    function toggleSidebar() {
        if (window.innerWidth <= 768) {
            // Mobile view
            sidebar.classList.toggle("expanded-mobile");
            sidebarOverlay.classList.toggle("active");
        } else {
            // Desktop view
            sidebar.classList.toggle("collapsed");
            content.classList.toggle("expanded");
        }
    }

    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener("click", toggleSidebar);
    }

    // Close sidebar when clicking on overlay (mobile)
    sidebarOverlay.addEventListener("click", function() {
        sidebar.classList.remove("expanded-mobile");
        sidebarOverlay.classList.remove("active");
    });

    // Adjust sidebar on window resize
    function adjustSidebarOnResize() {
        if (window.innerWidth <= 768) {
            // On mobile, ensure sidebar is collapsed by default and content is full width
            sidebar.classList.remove("collapsed"); // Remove desktop collapsed class
            sidebar.classList.remove("expanded-mobile"); // Ensure it's not expanded initially
            content.classList.remove("expanded"); // Ensure content is not pushed
            sidebarOverlay.classList.remove("active");
        } else {
            // On desktop, ensure sidebar is not expanded-mobile and content is adjusted
            sidebar.classList.remove("expanded-mobile");
            sidebarOverlay.classList.remove("active");
            // If sidebar was collapsed on desktop, keep it collapsed
            // Otherwise, ensure it's not collapsed and content is adjusted
            if (!sidebar.classList.contains("collapsed")) {
                content.classList.remove("expanded");
            }
        }
    }

    // Initial adjustment on load
    adjustSidebarOnResize();

    // Adjust on resize
    window.addEventListener("resize", adjustSidebarOnResize);

    // Active menu item
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll(".sidebar-menu li a");

    menuItems.forEach(item => {
        const href = item.getAttribute("href");
        if (href === currentPath || (href !== "/" && currentPath.startsWith(href))) {
            item.parentElement.classList.add("active");
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll("[data-bs-toggle=\"tooltip\"]"));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll("[data-bs-toggle=\"popover\"]"));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize datepickers
    const datepickers = document.querySelectorAll(".datepicker");
    if (datepickers.length > 0 && typeof flatpickr !== "undefined") {
        datepickers.forEach(function(el) {
            flatpickr(el, {
                dateFormat: "d/m/Y",
                locale: "pt"
            });
        });
    }

    // Copy to clipboard function for WhatsApp messages
    const copyButtons = document.querySelectorAll(".copy-message");
    copyButtons.forEach(button => {
        button.addEventListener("click", function() {
            const messageId = this.getAttribute("data-message");
            const messageText = document.getElementById(messageId).innerText;

            navigator.clipboard.writeText(messageText).then(() => {
                // Show success message
                const originalText = this.innerHTML;
                this.innerHTML = "<i class=\"fas fa-check\"></i> Copiado!";
                this.classList.add("btn-success");
                this.classList.remove("btn-primary");

                // Reset button after 2 seconds
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove("btn-success");
                    this.classList.add("btn-primary");
                }, 2000);
            });
        });
    });
});


