function calculateCVSS() {
    const exploitabilityCoefficient = 8.22;
    const scopeCoefficient = 1.08;

    const AV = { N: 0.85, A: 0.62, L: 0.55, P: 0.2 };
    const AC = { H: 0.44, L: 0.77 };
    const PR = { U: { N: 0.85, L: 0.62, H: 0.27 }, C: { N: 0.85, L: 0.68, H: 0.5 } };
    const UI = { N: 0.85, R: 0.62 };
    const S = { U: 6.42, C: 7.52 };
    const CIA = { N: 0, L: 0.22, H: 0.56 };

    // let av = $('#attack-vector').val();
    // let ac = $('#attack-complexity').val();
    // let pr = $('#privileges-required').val();
    // let ui = $('#user-interaction').val();
    // let s = $('#scope').val();
    // let c = $('#confidentiality-impact').val();
    // let i = $('#integrity-impact').val();
    // let a = $('#availability-impact').val();

    // Lấy giá trị từ radio button
    let av = $('input[name="attack-vector"]:checked').val();
    let ac = $('input[name="attack-complexity"]:checked').val();
    let pr = $('input[name="privileges-required"]:checked').val();
    let ui = $('input[name="user-interaction"]:checked').val();
    let s = $('input[name="scope"]:checked').val();
    let c = $('input[name="confidentiality-impact"]:checked').val();
    let i = $('input[name="integrity-impact"]:checked').val();
    let a = $('input[name="availability-impact"]:checked').val();

    // $('#id_risk_av').val(av);
    // $('#id_risk_ac').val(ac);
    // $('#id_risk_pr').val(pr);
    // $('#id_risk_ui').val(ui);
    // $("#risk-av").text(av);
    // $("#risk-ac").text(ac);
    // $("#risk-pr").text(pr);
    // $("#risk-ui").text(ui);

    // Mapping sang dạng thân thiện
    let av_mapping = { "N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical" };
    let ac_mapping = { "L": "Low", "H": "High" };
    let pr_mapping = { "N": "None", "L": "Low", "H": "High" };
    let ui_mapping = { "N": "None", "R": "Required" };

    // Áp dụng mapping, nếu không tìm thấy thì giữ nguyên giá trị cũ
    let av_text = av_mapping[av] || av;
    let ac_text = ac_mapping[ac] || ac;
    let pr_text = pr_mapping[pr] || pr;
    let ui_text = ui_mapping[ui] || ui;

    // Cập nhật giá trị vào input hidden (để gửi lên server)
    $('#id_risk_av').val(av_text);
    $('#id_risk_ac').val(ac_text);
    $('#id_risk_pr').val(pr_text);
    $('#id_risk_ui').val(ui_text);

    // Cập nhật giao diện hiển thị với giá trị đã mapping
    $("#risk-av").text(av_text);
    $("#risk-ac").text(ac_text);
    $("#risk-pr").text(pr_text);
    $("#risk-ui").text(ui_text);


    let impactSubScoreMultiplier = (1 - ((1 - CIA[c]) * (1 - CIA[i]) * (1 - CIA[a])));
    let impactSubScore;
    if (s === 'U') {
        impactSubScore = S[s] * impactSubScoreMultiplier;
    } else {
        impactSubScore = S[s] * (impactSubScoreMultiplier - 0.029) - (3.25 * Math.pow(impactSubScoreMultiplier - 0.02, 15));
    }

    let exploitability = exploitabilityCoefficient * AV[av] * AC[ac] * PR[s][pr] * UI[ui];
    let baseScore;
    
    if (impactSubScore <= 0) {
        baseScore = 0;
    } else {
        if (s === 'U') {
            baseScore = Math.min((impactSubScore + exploitability), 10);
        } else {
            baseScore = Math.min((impactSubScore + exploitability) * scopeCoefficient, 10);
        }
    }

    function roundUp1(value) {
        return Math.ceil(value * 10) / 10;
    }
    baseScore = roundUp1(baseScore);

    // baseScore = Math.round(baseScore * 10) / 10;

    let rating = baseScore >= 9 ? "Critical" :
             baseScore >= 7 ? "High" :
             baseScore >= 4 ? "Medium" :
             baseScore > 0 ? "Low" : "Recommend";

    let vector = `CVSS:3.1/AV:${av}/AC:${ac}/PR:${pr}/UI:${ui}/S:${s}/C:${c}/I:${i}/A:${a}`;

    $("#risk-score").text(baseScore);
    $("#risk-rating").text(rating).removeClass("text-danger text-warning text-success")
        .addClass(rating === "High" || rating === "Critical" ? "text-danger" : rating === "Medium" ? "text-warning" : "text-success");
    $("#cvss-vector").text(vector);

    // Cập nhật nội dung hiển thị
    $("#risk-score").text(baseScore);
    $("#risk-rating").text(rating);
    $("#risk-vector").text(vector);

    // Xóa tất cả class màu cũ trước khi thêm mới
    $("#risk-rating, #risk-score").removeClass("critical_text high_text medium_text low_text recommend_text");

    // $("#risk-rating").removeClass("critical_text high_text medium_text low_text recommend_text");
    // $("#risk-score").removeClass("critical_text high_text medium_text low_text recommend_text");

    // Thêm class tương ứng với risk rating
    // if (rating === "Critical") {
    //     $("#risk-rating").addClass("critical_text");
    //     $("#risk-score").addClass("critical_text");
    // } else if (rating === "High") {
    //     $("#risk-rating").addClass("high_text");
    //     $("#risk-score").addClass("high_text");
    // } else if (rating === "Medium") {
    //     $("#risk-rating").addClass("medium_text");
    //     $("#risk-score").addClass("medium_text");
    // } else if (rating === "Low") {
    //     $("#risk-rating").addClass("low_text");
    //     $("#risk-score").addClass("low_text");
    // } else {
    //     $("#risk-rating").addClass("recommend_text");
    //     $("#risk-score").addClass("recommend_text");
    // }
    switch (rating) {
        case "Critical":
            $("#risk-rating, #risk-score").addClass("critical_text");
            break;
        case "High":
            $("#risk-rating, #risk-score").addClass("high_text");
            break;
        case "Medium":
            $("#risk-rating, #risk-score").addClass("medium_text");
            break;
        case "Low":
            $("#risk-rating, #risk-score").addClass("low_text");
            break;
        case "Recommend":
            $("#risk-rating, #risk-score").addClass("recommend_text");
            break;
    }
    // lưu vào form
    $("#VulnerabiityForm").on("submit", function () {
    $("#risk-rating-input").val($("#risk-rating").text().trim());
    $("#risk-score-input").val($("#risk-score").text().trim());
    $("#risk-vector-input").val($("#risk-vector").text().trim());
});


}