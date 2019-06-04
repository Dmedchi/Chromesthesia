window.onload = function () {
    $('.basket-list').on('change', 'input[type="number"]', function (event) {
        let tareget = event.target;

        $.ajax({
            url: "/basket/update/" + tareget.name + "/" + tareget.value + "/",
            success: function (data) {
                $('.basket-list').html(data.result);
            },
        });

        event.preventDefault();

    });
};
