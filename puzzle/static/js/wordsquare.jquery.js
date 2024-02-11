(function( $ ) {

    class Slot {

        constructor(letter, isOpen) {
            this.letter = letter;
            this.isOpen = isOpen;
            this.slotType = this.letter === " " ? 'guess' : 'slot';
        }

    }

    class Hint {

        constructor(id, letter, isOpen) {
            this.id = 'hint-' + id;
            this.letter = letter;
            this.isOpen = isOpen;
            this.isSelected = false;
        }

    }

    class Guess extends Slot {

        constructor(letter, isOpen, hint=null) {
            super(letter, isOpen);
            this.hint = hint;
        }

    }

    class WordSquareApi {
        constructor(settings) {
            this.wrapper = settings.wrapper;
            this.hintsWrapper = settings.hintsWrapper;
            this.startButton = settings.startButton;
            this.apiUrl = settings.apiUrl;
            this.data = null;
            this.hints = null;
            this.solution = null;
            this.guesses = null;
            this.grid = null;
            this.selectedHint = null;
        }

        init(){
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
                if (self.data[row][column].slotType !== "guess") {
                    return;
                }
                let cell = content.parents('td');
                let guess = self.guesses[row][column];
                if (guess.hint) {
                    let hint = guess.hint;
                    hint.isOpen = true;
                    guess.letter = ' ';
                    guess.hint = null;
                    guess.isOpen = true;
                }
                else {
                    guess.letter = cell.hasClass('letter-add') && self.selectedHint ? self.selectedHint.letter : ' ';
                    guess.hint = cell.hasClass('letter-add') && self.selectedHint ? self.selectedHint : null;
                    guess.isOpen = false;
                    if (self.selectedHint) {
                        self.selectedHint.isOpen = false;
                    }
                }
                cell.toggleClass('letter-add');
                self.updateGrid(self.guesses);
                self.updateHints();
                if (self.solutionOK()) {
                    self.updateGrid(self.solution);
                    alert("You solved the puzzle!");
                }
            });
            this.hintsWrapper.on('click', '.hint', function () {
                let hint = self.findHint($(this).data('hint-id'));
                if (!hint.isOpen) {
                    return;
                }
                $('.hint').removeClass('letter-selected');
                self.selectedHint = hint.isSelected ? null : hint;
                if (!hint.isSelected) {
                    $(this).addClass('letter-selected');
                    $('.letter-open').parents('td').addClass('letter-add');
                }
                else {
                    $('.letter-open').parents('td').removeClass('letter-add');
                }
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
                        self.data = self.dataToSlots(res.puzzleData.data);
                        self.hints = self.dataToHints(res.puzzleData.hints);
                        self.solution = self.dataToSolution(res.puzzleData.solution);
                        self.guesses = self.dataToGuesses(res.puzzleData.data);
                        self.updateGrid(self.data);
                        self.updateHints();
                    }
                });
            }).trigger('init');
        }

        dataToSlots(data) {
            let slots= [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(new Slot(letter, letter === " "));
                }
                slots.push(row);
            }
            return slots;
        }

        dataToHints(data) {
            let hints = [];
            for (let i = 0; i < data.length; i++) {
                hints.push(new Hint("" + i, data[i], true));
            }
            return hints;
        }

        dataToGuesses(data) {
            let guesses= [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii];
                    row.push(new Guess(letter, letter === " "));
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
                    row.push(new Slot(letter, false));
                }
                solution.push(row);
            }
            return solution;
        }

        findHint(hintId) {
            for (let i = 0; i < this.hints.length; i++) {
                if (this.hints[i].id === hintId) {
                    return this.hints[i];
                }
            }
            return null;
        }

        updateGrid(data) {
            this.grid.updateConfig({
                data: this.getGridData(data)
            }).forceRender();
        }

        updateHints() {
            this.hintsWrapper.empty();
            for (let i = 0; i < this.hints.length; i++) {
                let hint = this.hints[i];
                let clss = ["hint"];
                if (!hint.isOpen) {
                    clss.push("letter-used");
                }
                if (hint.isSelected) {
                    clss.push("letter-selected");
                }
                let cls = clss.join(" ");
                this.hintsWrapper.append('<div data-hint-id="' + hint.id + '" data-hint="' + hint.letter + '" class="' + cls + '">' + hint.letter + '</div>');
            }
        }

        getGridData(data) {
            let gridData = [];
            for (let i = 0; i < data.length; i++) {
                let row = [];
                for (let ii = 0; ii < data[i].length; ii++) {
                    let letter = data[i][ii].letter;
                    let clss = [];
                    if (data[i][ii].slotType === 'guess') {
                        clss.push("letter-guess");
                    }
                    if (data[i][ii].isOpen) {
                        clss.push("letter-open");
                    }
                    let cls = clss.length ? ' class="' + clss.join(' ') + '"' : "";
                    row.push(
                        gridjs.html(
                            '<div' + cls + ' data-column="' + ii + '" data-row="' + i + '" data-letter="' + letter + '">' +
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
                    if (this.solution[i][ii].letter !== this.guesses[i][ii].letter) {
                        return false;
                    }
                }
            }
            return true;
        }
    }

    $.fn.wordSquare = function(settings) {

        let wordSquareApi = new WordSquareApi({
            wrapper: $(this).find('#wrapper'),
            hintsWrapper: $(this).find('#hints'),
            startButton: $(this).find('#start'),
            apiUrl: settings.apiUrl
        });
        wordSquareApi.init();

        return this;

    };

}( jQuery ));