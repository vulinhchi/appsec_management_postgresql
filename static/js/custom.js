// chức năng vuln template:
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.querySelector('input[name="name_vuln"]'); // Chọn ô nhập liệu
    const suggestionsList = document.getElementById('vuln_suggestions'); // Chọn danh sách gợi ý

    // Lắng nghe sự kiện input để tìm kiếm gợi ý
    inputField.addEventListener('input', function () {
        const query = inputField.value.trim(); // Lấy giá trị người dùng nhập

        if (!query) {
            suggestionsList.style.display = 'none';
            suggestionsList.innerHTML = ''; // Xóa gợi ý cũ
            return;
        }

        // Gửi yêu cầu AJAX để tìm kiếm các gợi ý
        fetch(`/pentest/get_vuln_template_suggestions/?query=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsList.innerHTML = ''; // Xóa các gợi ý cũ
                if (data.results && data.results.length > 0) {
                    suggestionsList.style.display = 'block'; // Hiển thị danh sách

                    // Lặp qua các kết quả trả về và tạo <li> cho mỗi kết quả
                    data.results.forEach(result => {
                        const li = document.createElement('li');
                        li.classList.add('list-group-item');
                        li.textContent = result.name_vuln;
                        // Thêm sự kiện khi người dùng chọn gợi ý
                        li.addEventListener('click', () => {
                            inputField.value = result.name_vuln;

                            // Cập nhật các input
                            document.querySelector('[name="description"]').value = result.description || '';
                            document.querySelector('[name="impact"]').value = result.impact || '';
                            document.querySelector('[name="recommendation"]').value = result.recommendation || '';
                            document.querySelector('[name="reference"]').value = result.reference || '';

                            document.querySelector('[name="likelihood_rate"]').value = result.likelihood_rate || '';
                            document.querySelector('[name="impact_rate"]').value = result.impact_rate || '';
                            // 👇 Thêm đoạn này để cập nhật các thẻ hiển thị
                            document.getElementById('risk-score').textContent = result.risk_score || '';
                            document.getElementById('risk-rating').textContent = result.risk_rating || '';
                            document.getElementById('risk-vector').textContent = result.risk_vector || '';

                            // 👇 Cập nhật input hidden để gửi về backend nếu cần
                            document.getElementById('risk-score-input').value = result.risk_score || '';
                            document.getElementById('risk-rating-input').value = result.risk_rating || '';
                            document.getElementById('risk-vector-input').value = result.risk_vector || '';

                            // Nếu cần cập nhật class cho màu sắc Risk Rating (như critical_text / medium_text), thì reset lại class
                            const ratingSpan = document.getElementById('risk-rating');
                            const scoreSpan = document.getElementById('risk-score');
                            ratingSpan.className = 'info-box-text text-center mb-0'; // reset
                            scoreSpan.className = 'info-box-text text-center mb-0';
                            if (result.risk_rating === 'Critical') ratingSpan.classList.add('critical_text');
                            else if (result.risk_rating === 'High') ratingSpan.classList.add('high_text');
                            else if (result.risk_rating === 'Medium') ratingSpan.classList.add('medium_text');
                            else if (result.risk_rating === 'Low') ratingSpan.classList.add('low_text');
                            else if (result.risk_rating === 'Recommend') ratingSpan.classList.add('recommend_text');

                            if (result.risk_rating === 'Critical') scoreSpan.classList.add('critical_text');
                            else if (result.risk_rating === 'High') scoreSpan.classList.add('high_text');
                            else if (result.risk_rating === 'Medium') scoreSpan.classList.add('medium_text');
                            else if (result.risk_rating === 'Low') scoreSpan.classList.add('low_text');
                            else if (result.risk_rating === 'Recommend') scoreSpan.classList.add('recommend_text');
                        });

                        suggestionsList.appendChild(li); // Thêm phần tử vào danh sách
                    });
                } else {
                    suggestionsList.style.display = 'none'; // Ẩn danh sách nếu không có kết quả
                }
            })
            .catch(error => {
                console.error('Error fetching vulnerability suggestions:', error);
            });
    });
});



// chức năng search
$(document).ready(function() {
    function parseDate(dateString) {
        // console.log(dateString)
        if (!dateString) return null;

        // 🔹 Hỗ trợ YYYY-MM-DD
        var parts = dateString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (parts) {
            return new Date(parts[1], parts[2] - 1, parts[3]); 
        }

        // 🔹 Hỗ trợ DD/MM/YYYY
        parts = dateString.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
        if (parts) {
            return new Date(parts[3], parts[2] - 1, parts[1]); 
        }

        // 🔹 Hỗ trợ "March 10, 2024"
        var parsedDate = Date.parse(dateString);
        if (!isNaN(parsedDate)) {
            return new Date(parsedDate);
        }

        return null; 
    }

    function filterTable() {
        var startDateInput = $("#start-date-from").val();
        var endDateInput = $("#end-date-to").val();
        var startDate = parseDate(startDateInput);
        var endDate = parseDate(endDateInput);

        // search in all vuln
        var startDateInputVuln = $("#start-date-vuln").val();
        var endDateInputVuln = $("#end-date-vuln").val();
        var startDateVuln = parseDate(startDateInputVuln);
        var endDateVuln = parseDate(endDateInputVuln);
        
        // ===== Filter AppSecTask + PentestTask + VerifyTask =====
        $("#taskTable tbody tr").each(function () {
            var row = $(this);
            var isValid = true;
            var taskStartDateText = row.find("td").filter(function(i) {
                return $("#taskTable thead th").eq(i).text().trim().startsWith("Start Date");
            }).text().trim();

            var taskEndDateText = row.find("td").filter(function(i) {
                return $("#taskTable thead th").eq(i).text().trim().startsWith("End Date");
            }).text().trim();

            var taskStartDate = parseDate(taskStartDateText);
            var taskEndDate = parseDate(taskEndDateText);
            
            if (startDate && taskStartDate && taskStartDate < startDate) {
                isValid = false;
            }
            if (endDate && taskEndDate && taskEndDate > endDate) {
                isValid = false;
            }

            // 🔍 Lấy Notify Date từ cột thứ 8 (index = 7)
            var notifyIndex = row.find("td").filter(function(i) {
                return $("#taskTable thead th").eq(i).text().trim().startsWith("Notify date");
            }).text().trim();

            console.log("NOTIFY: " , notifyIndex)
            // Lấy Notify Date đúng từ cột đó trong row hiện tại
            var notifyDateText = row.find("td").eq(notifyIndex).text().trim();
            var notifyDate = parseDate(notifyDateText);
        
            // === Lọc theo khoảng Notify Date ===
            if (startDateVuln && notifyDate && notifyDate < startDateVuln) {
                isValid = false;
            }
            if (endDateVuln && notifyDate && notifyDate > endDateVuln) {
                isValid = false;
            }
            
            $(".filter-input").each(function () {
                var columnIndex = $(this).data("column");
                var filterValue = $(this).val().toLowerCase().trim();
                var cellText = row.find(`td:nth-child(${columnIndex + 1})`).text().toLowerCase().trim();
                if (filterValue && !cellText.includes(filterValue)) {
                    isValid = false;
                }
            });

            row.toggle(isValid);
        });

        
    }

    // ✅ Chạy filter khi nhập input hoặc chọn ngày
    $(".filter-input, .filter-date, .filter-date-vuln").on("input change", filterTable);

    // ✅ Nút Clear Filters
    $("#clearFilters").on("click", function() {
        $(".filter-input, .filter-date, .filter-date-vuln").val("").trigger("change");
        filterTable();
    });


    // ✅ Khi trang load, filter chạy 1 lần để đảm bảo không lỗi
    filterTable();
});

// tính năng sort theo cột:
let currentSortCol = null;
let sortAsc = true;

function sortTable(colIndex) {
    const table = document.getElementById("taskTable");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);

    // Toggle sort direction nếu click cùng 1 cột
    if (currentSortCol === colIndex) {
        sortAsc = !sortAsc;
    } else {
        sortAsc = true;
        currentSortCol = colIndex;
    }

    rows.sort((a, b) => {
        const aText = a.cells[colIndex].innerText.trim().toLowerCase();
        const bText = b.cells[colIndex].innerText.trim().toLowerCase();

        if (!isNaN(aText) && !isNaN(bText)) {
            return (parseFloat(aText) - parseFloat(bText)) * (sortAsc ? 1 : -1);
        }

        return aText.localeCompare(bText) * (sortAsc ? 1 : -1);
    });

    rows.forEach(row => tbody.appendChild(row));

    // Reset tất cả mũi tên
    const thElements = table.querySelectorAll("thead th");
    thElements.forEach((th, i) => {
        if (i !== colIndex) {
            th.innerHTML = th.innerHTML.replace(/[\u25B2\u25BC]/g, ''); // remove ▲▼
        }
    });

    // Thêm mũi tên vào cột hiện tại
    const th = thElements[colIndex];
    const arrow = sortAsc ? " ▲" : " ▼";
    th.innerHTML = th.innerHTML.replace(/[\u25B2\u25BC]/g, '') + arrow;
}

// checkbox
document.addEventListener("DOMContentLoaded", function () {
    let checkboxes = document.querySelectorAll(".column-toggle");

    function updateColumnVisibility() {
        checkboxes.forEach(checkbox => {
            let columnIndex = parseInt(checkbox.getAttribute("data-column"));

            // Lặp qua tất cả các hàng để hiển thị/ẩn cột
            document.querySelectorAll(`#taskTable thead th:nth-child(${columnIndex + 1}),
                                       #taskTable tbody td:nth-child(${columnIndex + 1})`).forEach(el => {
                el.style.display = checkbox.checked ? "" : "none";
            });
        });
    }

    // 🟢 Khi checkbox thay đổi
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateColumnVisibility);
    });

    // 🟢 Ẩn các cột khi load trang lần đầu
    updateColumnVisibility();
});

//hiển thị field điền theo form-control trong create_appsec_task.html
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#appSecTaskForm input, #appSecTaskForm select, #appSecTaskForm textarea").forEach(el => {
        el.classList.add("form-control");
    });
});
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#VulnerabiityForm input, #VulnerabiityForm select, #VulnerabiityForm textarea").forEach(el => {
        el.classList.add("form-control");
    });
});


// hiển thị number of apis khi nhập scope
// Hàm đếm số dòng
function countAPIs(scopeText) {
    // Tính số dòng trong scope (có thể tùy chỉnh logic này)
    const lines = scopeText.split('\n');
    return lines.length;
}

// Lắng nghe sự thay đổi của textarea (scope)
document.getElementById('id_scope').addEventListener('input', function() {
    const scopeText = this.value;
    const numberOfAPIs = countAPIs(scopeText);

    // Cập nhật giá trị của field "number_of_apis"
    document.getElementById('id_number_of_apis').value = numberOfAPIs;
});

// override upload file, k cho up lên imgur
window.addEventListener('DOMContentLoaded', () => {
  if (typeof $.fn.markdown !== 'undefined') {
    // Monkey patch để ép URL uploader về local (dù imgur: true)
    $.fn.markdown.Constructor.defaults.imgUpload = true;
    $.fn.markdown.Constructor.defaults.uploadUrl = '/api/uploader/';  // hoặc dùng biến martor_upload_url
    $.fn.markdown.Constructor.defaults.uploadMethod = 'POST';
    $.fn.markdown.Constructor.defaults.uploadFieldName = 'markdown-image-upload';
  }
});

// Affected URL, cho xóa dòng mới chưa lưu DB

document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById("add-form-btn");
    const formsetBody = document.getElementById("formset-body");
    const totalForms = document.getElementById("id_form-TOTAL_FORMS");
    const emptyFormRow = document.querySelector("#empty-form-template .form-row");

    if (!totalForms) {
        console.error('Không tìm thấy phần tử totalForms!');
        return;
    }

    // Hàm khởi tạo lại Martor editor cho tất cả các textarea chưa khởi tạo
    function reinitializeMartorEditors() {
        // Lặp qua tất cả các textarea chứa data-martor chưa được khởi tạo
        document.querySelectorAll("textarea[data-martor]:not(.martor-init)").forEach(function (el) {
            // Khởi tạo Martor cho textarea
            $(el).martor();
            // Đánh dấu textarea đã được khởi tạo để tránh khởi tạo lại
            el.classList.add("martor-init");
        });
    }

    // Thêm form mới khi bấm nút
    addBtn.addEventListener("click", function () {
        const formCount = parseInt(totalForms.value);
        const newRow = emptyFormRow.cloneNode(true);

        // Thay __prefix__ bằng index mới
        newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, formCount);

        // Gán lại ID cho row mới
        newRow.id = `form-row-${formCount}`;

        // Thêm vào DOM
        formsetBody.appendChild(newRow);

        // Cập nhật số lượng form
        totalForms.value = formCount + 1;

        // Re-init markdown editor
        reinitializeMartorEditors();
    });

    // Xoá form
    formsetBody.addEventListener("click", function (event) {
        if (event.target && event.target.classList.contains("remove-form-btn")) {
            const row = event.target.closest(".form-row");

            const deleteInput = row.querySelector("input[type='hidden'][name$='-DELETE']");
            if (deleteInput) {
                // Nếu có input DELETE, đánh dấu để xoá
                deleteInput.value = "on";
                row.style.display = "none";
            } else {
                // Form mới thì xoá trực tiếp
                row.remove();

                // Giảm total_forms
                const formCount = parseInt(totalForms.value);
                totalForms.value = formCount - 1;
            }
        }
    });

    // Khởi tạo martor khi trang tải lần đầu
    reinitializeMartorEditors();
});



