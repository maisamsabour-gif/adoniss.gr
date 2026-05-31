/**
 * Auto-convert text inputs for color fields to HTML5 color pickers
 */
document.addEventListener('DOMContentLoaded', function () {
    // Find inputs that contain color hex values
    const colorFields = ['heading_color', 'body_color'];

    colorFields.forEach(function (fieldName) {
        const input = document.getElementById('id_' + fieldName);
        if (!input) return;

        // Create a wrapper
        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.gap = '10px';

        // Create color picker
        const picker = document.createElement('input');
        picker.type = 'color';
        picker.value = input.value || '#000000';
        picker.style.width = '50px';
        picker.style.height = '38px';
        picker.style.border = '2px solid #d1d9e6';
        picker.style.borderRadius = '8px';
        picker.style.cursor = 'pointer';
        picker.style.padding = '2px';

        // Create preview swatch
        const preview = document.createElement('span');
        preview.style.display = 'inline-block';
        preview.style.width = '120px';
        preview.style.padding = '6px 12px';
        preview.style.borderRadius = '6px';
        preview.style.fontSize = '13px';
        preview.style.fontWeight = '600';
        preview.style.textAlign = 'center';
        preview.style.letterSpacing = '0.03em';
        preview.textContent = input.value;
        preview.style.background = input.value;
        preview.style.color = isLight(input.value) ? '#000' : '#fff';

        // Sync color picker → text input
        picker.addEventListener('input', function () {
            input.value = picker.value;
            preview.textContent = picker.value;
            preview.style.background = picker.value;
            preview.style.color = isLight(picker.value) ? '#000' : '#fff';
        });

        // Sync text input → color picker
        input.addEventListener('input', function () {
            if (/^#[0-9A-Fa-f]{6}$/.test(input.value)) {
                picker.value = input.value;
                preview.textContent = input.value;
                preview.style.background = input.value;
                preview.style.color = isLight(input.value) ? '#000' : '#fff';
            }
        });

        // Insert after the input
        input.parentNode.insertBefore(wrapper, input.nextSibling);
        wrapper.appendChild(picker);
        wrapper.appendChild(preview);
    });

    function isLight(hex) {
        hex = hex.replace('#', '');
        var r = parseInt(hex.substr(0, 2), 16);
        var g = parseInt(hex.substr(2, 2), 16);
        var b = parseInt(hex.substr(4, 2), 16);
        return (r * 299 + g * 587 + b * 114) / 1000 > 150;
    }
});
