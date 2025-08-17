// static/js/user-dropdown.js
$(document).ready(function () {
    var dropdownTimer;

    $('#userDropdown').hover(
        function () {
            // 鼠标悬停时显示下拉菜单
            clearTimeout(dropdownTimer);
            $('.dropdown-menu').removeClass('show');
            $(this).next('.dropdown-menu').addClass('show');
        },
        function () {
            // 鼠标离开时设置延迟隐藏
            var $dropdown = $(this).next('.dropdown-menu');
            dropdownTimer = setTimeout(function () {
                $dropdown.removeClass('show');
            }, 300);
        }
    );

    $('.dropdown-menu').hover(
        function () {
            // 鼠标悬停在下拉菜单上时取消隐藏
            clearTimeout(dropdownTimer);
        },
        function () {
            // 鼠标离开下拉菜单时隐藏
            $(this).removeClass('show');
        }
    );
});
