(function( $ ) {

    class WordFinderApi {
        constructor(settings) {
            this.wrapper = settings.wrapper;
            this.hintsWrapper = settings.hintsWrapper;
            this.startButton = settings.startButton;
            this.guessButton = settings.guessButton;
            this.solutionField = settings.solutionField;
            this.apiUrl = settings.apiUrl;
            this.data = null;
            this.words = null;
            this.hints = null;
            this.solution = null;
            this.state = null;
            this.grid = null;
        }

        init() {
            let self = this;

            this.grid = new gridjs.Grid({
                data: []
            });
            this.grid.render(this.wrapper.get(0));
            this.grid.on('cellClick', function (event) {
                let content = $(event.target);
                let row = parseInt(content.data('row'), 10);
                let column = parseInt(content.data('column'), 10);
                if (isNaN(row) || isNaN(column)) {
                    return;
                }
                let cell = content.parents('td');
                self.state[row][column] = cell.hasClass('letter-used') ? ' ' : self.data[row][column];
                cell.toggleClass('letter-used');
                self.checkWords();
            });
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
                        self.words = res.puzzleData.words;
                        self.hints = res.puzzleData.hints;
                        self.solution = res.puzzleData.solution;
                        self.state = [];
                        for (let i = 0; i < self.data.length; i++) {
                            let row = [];
                            for (let ii = 0; ii < self.data[i].length; ii++) {
                                row.push(" ");
                            }
                            self.state.push(row);
                        }
                        self.updateGrid(self.data);
                        self.updateHints(self.hints);
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

        updateGrid(data) {
            this.grid.updateConfig({
                data: this.getGridData(data)
            }).forceRender();
        }

        updateHints(hints) {
            this.hintsWrapper.empty();
            for (let i = 0; i < hints.length; i++) {
                let hint = hints[i];
                this.hintsWrapper.append('<div data-hint="' + hint + '" class="hint">' + hint + '</div>');
            }
        }

        getGridData(data) {
            let gridData = [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(
                        gridjs.html(
                            '<div class="letter" data-column="' + ii + '" data-row="' + i + '" data-letter="' + letter + '">' +
                             letter +
                             '</div>'
                        )
                    );
                }
                gridData.push(row);
            }
            return gridData;
        }

        checkWords() {
            let to_keep = [];
            for (let i = 0; i < this.words.length; i++) {
                let word = '';
                for (let ii = 0; ii < this.words[i].length; ii++) {
                    let coords = this.words[i][ii];
                    word += this.state[coords[0]][coords[1]];
                }
                if ($('[data-hint="' + word + '"]').length) {
                    to_keep.push(word);
                }
            }
            $('.hint').removeClass('.letter-used');
            for (let i = 0; i < to_keep.length; i++) {
                $('[data-hint="' + to_keep[i] + '"]').addClass('letter-used');
            }
        }
    }

    $.fn.wordFinder = function(settings) {

        let wordFinderApi = new WordFinderApi({
            wrapper: $(this).find('#wrapper'),
            hintsWrapper: $(this).find('#hints'),
            startButton: $(this).find('#start'),
            guessButton: $(this).find('#guess'),
            solutionField: $(this).find('#solution'),
            apiUrl: settings.apiUrl
        });
        wordFinderApi.init();

        return this;

    };

}( jQuery ));