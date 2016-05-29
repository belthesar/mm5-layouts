'use strict';

const TimeObject = require('./classes/time-object');
let interval;

module.exports = function (nodecg) {
	const stopwatch = nodecg.Replicant('stopwatch', {
		defaultValue: (function () {
			const to = new TimeObject(0);
			to.state = 'stopped';
			to.results = [null, null, null, null];
			return to;
		})()
	});

	// Load the existing time and start the stopwatch at that.
	if (stopwatch.value.state === 'running') {
		const missedSeconds = (Date.now() - stopwatch.value.timestamp) / 1000;
		TimeObject.setSeconds(stopwatch.value, stopwatch.value.seconds + missedSeconds);
		start();
	}

	nodecg.listenFor('startTimer', start);
	nodecg.listenFor('stopTimer', stop);
	nodecg.listenFor('resetTimer', reset);
	nodecg.listenFor('completeRunner', completeRunner);
	nodecg.listenFor('resumeRunner', resumeRunner);
	nodecg.listenFor('editResult', editResult);

	/**
	 * Starts the timer.
	 * @returns {undefined}
	 */
	function start() {
		if (stopwatch.value.state === 'running') {
			return;
		}

		stopwatch.value.state = 'running';
		interval = setInterval(tick, 1000);
	}

	/**
	 * Increments the timer by one second.
	 * @returns {undefined}
	 */
	function tick() {
		TimeObject.increment(stopwatch.value);
	}

	/**
	 * Stops the timer.
	 * @returns {undefined}
	 */
	function stop() {
		clearInterval(interval);
		stopwatch.value.state = 'stopped';
	}

	/**
	 * Stops and resets the timer, clearing the time and results.
	 * @returns {undefined}
	 */
	function reset() {
		stop();
		TimeObject.setSeconds(stopwatch.value, 0);
		stopwatch.value.results = [];
	}

	/**
	 * Marks a runner as complete.
	 * @param {Number} index - The runner to modify (0-3).
	 * @param {Boolean} forfeit - Whether or not the runner forfeit.
	 * @returns {undefined}
	 */
	function completeRunner({index, forfeit}) {
		if (!stopwatch.value.results[index]) {
			stopwatch.value.results[index] = new TimeObject(stopwatch.value.raw);
		}

		stopwatch.value.results[index].forfeit = forfeit;
		recalcPlaces();
	}

	/**
	 * Marks a runner as still running.
	 * @param {Number} index - The runner to modify (0-3).
	 * @returns {undefined}
	 */
	function resumeRunner(index) {
		stopwatch.value.results[index] = null;
	}

	/**
	 * Edits the final time of a result.
	 * @param {Number} index - The result index to edit.
	 * @param {String} newTime - A hh:mm:ss (or mm:ss) formatted new time.
	 * @returns {undefined}
	 */
	function editResult({index, newTime}) {
		if (newTime && stopwatch.value.results[index]) {
			TimeObject.setSeconds(stopwatch.value.results[index], TimeObject.parseSeconds(newTime));
			recalcPlaces();
		}
	}

	/**
	 * Re-calculates the podium place for all runners.
	 * @returns {undefined}
	 */
	function recalcPlaces() {
		const finishedResults = stopwatch.value.results.filter(r => {
			if (r) {
				r.place = 0;
				return !r.forfeit;
			}

			return false;
		});

		finishedResults.sort((a, b) => {
			return a.raw - b.raw;
		});

		finishedResults.forEach((r, index) => {
			r.place = index + 1;
		});
	}
};
