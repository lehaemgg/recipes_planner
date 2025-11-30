document.addEventListener('DOMContentLoaded', function() {
    // Initialize ingredient counter
    let ingredientCount = document.querySelectorAll('.ingredient-form').length;
    let stepCount = document.querySelectorAll('.step-form').length;

    // Add ingredient function
    function addIngredient() {
        const container = document.getElementById('ingredient-forms');
        const emptyForm = document.getElementById('empty-ingredient-form').innerHTML;
        const formRegex = /__prefix__/g;
        const newForm = emptyForm.replace(formRegex, ingredientCount);
        
        const div = document.createElement('div');
        div.innerHTML = newForm;
        container.appendChild(div.firstElementChild);
        
        ingredientCount++;
        updateFormsetCount('ingredients', ingredientCount);
        M.updateTextFields();
    }

    // Add step function
    function addStep() {
        const container = document.getElementById('step-forms');
        const emptyForm = document.getElementById('empty-step-form').innerHTML;
        const formRegex = /__prefix__/g;
        const newForm = emptyForm.replace(formRegex, stepCount);
        
        const div = document.createElement('div');
        div.innerHTML = newForm;
        container.appendChild(div.firstElementChild);
        
        stepCount++;
        updateFormsetCount('steps', stepCount);
        M.updateTextFields();
        
        // Add photo preview to new form
        const newFileInput = div.querySelector('input[type="file"]');
        if (newFileInput) {
            addPhotoPreview(newFileInput);
        }
    }

    // Update formset management form
    function updateFormsetCount(prefix, count) {
        const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
        if (totalForms) {
            totalForms.value = count;
        }
    }

    // Photo preview function
    function addPhotoPreview(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = input.closest('.step-form').querySelector('.photo-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'photo-preview';
                        preview.style.marginTop = '10px';
                        input.closest('.file-field').appendChild(preview);
                    }
                    preview.innerHTML = `<img src="${e.target.result}" style="max-width: 200px; max-height: 200px;" class="responsive-img">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Remove form function
    function removeForm(button, formClass) {
        const form = button.closest(formClass);
        const deleteInput = form.querySelector('input[name$="-DELETE"]');
        if (deleteInput) {
            deleteInput.checked = true;
            form.style.display = 'none';
        } else {
            form.remove();
        }
    }

    // Event listeners
    document.getElementById('add-ingredient').addEventListener('click', addIngredient);
    document.getElementById('add-step').addEventListener('click', addStep);

    // Add photo preview to existing file inputs
    document.querySelectorAll('input[type="file"]').forEach(addPhotoPreview);

    // Remove button event listeners
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-ingredient')) {
            removeForm(e.target, '.ingredient-form');
        }
        if (e.target.classList.contains('remove-step')) {
            removeForm(e.target, '.step-form');
        }
    });

    // Save button handlers
    document.getElementById('save-recipe').addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('recipe-form').submit();
    });

    document.getElementById('save-and-close').addEventListener('click', function(e) {
        e.preventDefault();
        const form = document.getElementById('recipe-form');
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'save_and_close';
        input.value = '1';
        form.appendChild(input);
        form.submit();
    });




    
    // Helper function to add ingredient with data
    function addIngredientWithData(name, quantity, unit) {
        const container = document.getElementById('ingredient-forms');
        const emptyForm = document.getElementById('empty-ingredient-form').innerHTML;
        const formRegex = /__prefix__/g;
        const newForm = emptyForm.replace(formRegex, ingredientCount);
        
        const div = document.createElement('div');
        div.innerHTML = newForm;
        const formElement = div.firstElementChild;
        container.appendChild(formElement);
        
        // Fill in the data
        formElement.querySelector(`input[name="ingredients-${ingredientCount}-name"]`).value = name;
        formElement.querySelector(`input[name="ingredients-${ingredientCount}-quantity"]`).value = quantity;
        formElement.querySelector(`input[name="ingredients-${ingredientCount}-unit"]`).value = unit;
        
        ingredientCount++;
        updateFormsetCount('ingredients', ingredientCount);
        M.updateTextFields();
    }
    
    // Helper function to add step with data
    function addStepWithData(description) {
        const container = document.getElementById('step-forms');
        const emptyForm = document.getElementById('empty-step-form').innerHTML;
        const formRegex = /__prefix__/g;
        const newForm = emptyForm.replace(formRegex, stepCount);
        
        const div = document.createElement('div');
        div.innerHTML = newForm;
        const formElement = div.firstElementChild;
        container.appendChild(formElement);
        
        // Fill in the data
        formElement.querySelector(`textarea[name="steps-${stepCount}-description"]`).value = description;
        
        stepCount++;
        updateFormsetCount('steps', stepCount);
        M.updateTextFields();
        M.textareaAutoResize(formElement.querySelector('textarea'));
        
        // Add photo preview to new form
        const newFileInput = formElement.querySelector('input[type="file"]');
        if (newFileInput) {
            addPhotoPreview(newFileInput);
        }
    }
});