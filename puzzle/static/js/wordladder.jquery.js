(function( $ ) {

    class WordLadderApi {
        constructor(settings) {
            this.wrapper = settings.wrapper;
            this.guessField = settings.guessField;
            this.startButton = settings.startButton;
            this.guessButton = settings.guessButton;
            this.apiUrl = settings.apiUrl;
            this.data = null;
            this.solution = null;
            this.guesses = null;
            this.grid = null;
            this.activeGuess = null;
            this.pollGridProcess = null;
        }

        init(){
            let self = this;

            this.grid = new gridjs.Grid({
                data: []
            });
            this.grid.render(this.wrapper.get(0));
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
                        self.data = self.dataToSlots(res.puzzleData.data);
                        self.guessField.attr('max_length', self.data[0].length);
                        self.solution = self.dataToSolution(res.puzzleData.solution);
                        self.activeGuess = 1;
                        self.guesses = self.dataToGuesses(res.puzzleData.data);
                        self.pollGridProcess = setInterval(function () {
                            self.pollGrid();
                        }, 1000);
                        self.updateGrid(self.data);
                    }
                });
            }).trigger('init');
            this.guessButton.on('click', function (event) {
                let value = self.guessField.val().toUpperCase();
                let joined = self.solution[self.activeGuess].join("");
                for (let i = 0; i < self.guesses[self.activeGuess].length; i++) {
                    if (joined.substring(i, i + 1) === value.substring(i, i + 1)) {
                        self.guesses[self.activeGuess][i] = value.substring(i, i + 1);
                    }
                }
                if (value === joined) {
                    self.activeGuess += 1;
                }
                self.pollGridProcess = setInterval(function () {
                    self.pollGrid();
                }, 1000);
                self.updateGrid(self.guesses);
                if (self.solutionOK()) {
                    alert("You solved the puzzle!");
                }
            });
        }

        dataToSlots(data) {
            let slots= [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(letter);
                }
                slots.push(row);
            }
            return slots;
        }

        dataToGuesses(data) {
            let guesses= [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(letter);
                }
                guesses.push(row);
            }
            return guesses;
        }

        dataToSolution(data) {
            let solution = [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(letter);
                }
                solution.push(row);
            }
            return solution;
        }

        updateGrid(data) {
            this.grid.updateConfig({
                data: this.getGridData(data)
            }).forceRender();
        }

        pollGrid() {
            let gridRows = $('.wordladder tr.gridjs-tr');
            if (gridRows.length) {
                gridRows.removeClass('letter-active');
                if (this.activeGuess < this.guesses.length - 1) {
                    $(gridRows.get(this.activeGuess)).addClass('letter-active');
                }
                clearInterval(this.pollGridProcess);
            }
        }

        getGridData(data) {
            let gridData = [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    let cls = letter !== ' ' ? ' class="letter-added"' : '';
                    row.push(
                        gridjs.html(
                            '<div ' + cls + ' data-column="' + ii + '" data-row="' + i + '">' +
                            letter +
                            '</div>'
                        )
                    );
                }
                gridData.push(row);
            }
            return gridData;
        }

        solutionOK() {
            for (let i = 0; i < this.solution.length; i++) {
                for (let ii = 0; ii < this.solution[i].length; ii++) {
                    if (this.solution[i][ii] !== this.guesses[i][ii]) {
                        return false;
                    }
                }
            }
            return true;
        }
    }

    $.fn.wordLadder = function(settings) {

        let wordLadderApi = new WordLadderApi({
            wrapper: $(this).find('#wrapper'),
            guessField: $(this).find('#word'),
            startButton: $(this).find('#start'),
            guessButton: $(this).find('#guess'),
            apiUrl: settings.apiUrl
        });
        wordLadderApi.init();

        return this;

    };

}( jQuery ));