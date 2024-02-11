(function( $ ) {

    class ImagePuzzleApi {
        constructor(settings) {
            this.wrapper = settings.wrapper;
            this.startButton = settings.startButton;
            this.guessButton = settings.guessButton;
            this.solutionField = settings.solutionField;
            this.apiUrl = settings.apiUrl;
            this.imageWidth = settings.imageWidth;
            this.data = null;
            this.solution = null;
        }

        init() {
            let self = this;

            this.startButton.on('init click', function (event) {
                $.ajax({
                    type: "GET",
                    url: self.apiUrl,
                    dataType: 'json',
                    async: true,
                    headers: {
                        "Content-Type": "application/json"
                    },
                    success: function (res) {
                        self.data = res.puzzleData.data;
                        self.solution = res.puzzleData.solution;
                        self.updateImage(self.data);
                        self.guessButton.prop('disabled', false);
                    }
                });
            }).trigger('init');
            this.guessButton.on('click', function (event) {
                if (self.solutionField.val().toUpperCase() === self.solution) {
                    alert('You guessed the word!');
                    self.guessButton.prop('disabled', true);
                }
            });
        }

        updateImage(data) {
            this.wrapper.html('<img src="data:image/jpeg;base64,' + data + '" alt="puzzle" width="' + this.imageWidth + '">');
        }

    }

    $.fn.imagePuzzle = function(settings) {

        let imagePuzzleApi = new ImagePuzzleApi({
            wrapper: $(this).find('#wrapper'),
            startButton: $(this).find('#start'),
            guessButton: $(this).find('#guess'),
            solutionField: $(this).find('#solution'),
            apiUrl: settings.apiUrl,
            imageWidth: settings.imageWidth
        });
        imagePuzzleApi.init();

        return this;

    };

}( jQuery ));