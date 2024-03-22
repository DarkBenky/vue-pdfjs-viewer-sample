<template>
	<div>
		<!-- testing of image calculation -->
		<!-- <button @click="calculateRealPosition">test</button> -->
		<div>
			<button @click="handlePrevious">Previous</button>
			<button @click="handleNext">Next</button>
			<p>{{ page_number }} / {{ numberOfPages }} page</p>

			<input id="pageNumber-input" type="number" />
			<button @click="handlePageChange">Go to page</button>
		</div>
		<button @click="handlePost">export</button>
	</div>
	<div @mousemove="handleDragging" @mousedown="handleDraggingStop">
		<h1>i am asking my self</h1>
		<canvas ref="canvas" id="theCanvas" @click="handleCanvasClick" @mousemove="handleMouseMove"
			@mouseup="handleMouseUp" @mousedown="handleMouseDown"></canvas>
		<button @click="addOverlay">add overlay</button>
		<div id="redOverlay" ref="redOverlay"></div>
		<div id="BgOverlay" ref="BgOverlay"></div>
		<input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" />
	</div>
	<div v-for="(overlay, index) in this.overlays" :key="index">
		<div :ref="overlay.ID" v-if="overlay.page_number === this.page_number" @mousedown="handleDragStart(index)"
			:style="{
				left: overlay.left,
				top: overlay.top,
				width: overlay.width,
				height: overlay.height,
				position: 'absolute',
				backgroundImage: 'url(' + overlay.low_res_img + ')',
				backgroundSize: 'contain',
				backgroundRepeat: 'no-repeat',
				backgroundPosition: 'center',
				opacity: '0.4',
				pointerEvents: overlay.pointerEvents,
				border: overlay.border_color,
			}">
		</div>
	</div>
	<!-- <div v-if="this.realPoint"> -->
	<!-- debugging of img position -->
	<!-- <div v-for="(box, index) in this.realPoint" :key="index"> -->
	<!-- <p>{{ box }}</p> -->
	<!-- <div v-if="box.page === this.page_number" :style="{ -->
	<!-- left: box.left + 'px', -->
	<!-- top: box.top + 'px', -->
	<!-- width: box.width + 'px', -->
	<!-- height: box.height + 'px', -->
	<!-- position: 'absolute', -->
	<!-- backgroundColor: 'red', -->
	<!-- opacity: '0.4', -->
	<!-- pointerEvents: 'none', -->
	<!-- }"> -->
	<!-- </div> -->
	<!-- </div> -->
	<!-- </div> -->
	<div v-for="(overlay, index) in this.overlays" :key="index">
		<div v-if="overlay.page_number === this.page_number" :style="{
				backgroundImage: 'url(' + overlay.low_res_img + ')',
				backgroundSize: 'contain',
				backgroundRepeat: 'no-repeat',
				backgroundPosition: 'center',
				height: '100px',
				width: '100px'
			}">
			<button @click="handleEdit(index)">edit</button>
			<div v-if="this.currentEdit === index">
				<button @click="delete_image(index)">delete</button>
				<button @click="handleScaling(index, 0.75)">-</button>
				<button @click="handleScaling(index, 1.25)">+</button>
			</div>
		</div>
	</div>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.mjs";
import axios from 'axios';

export default {
	name: "App",
	components: {},
	data() {
		return {
			pdfPath: "big-pdf.pdf",
			low_res_img: NaN,
			overlays: [],
			offsetX: 0,
			offsetY: 0,
			isDragging: false,
			overlay: false,
			left: 0,
			top: 0,
			width: 0,
			height: 0,
			currentImage: NaN,
			currentEdit: NaN,
			dragging: false,
			indexDraggedImg: NaN,
			page_number: 1,
			numberOfPages: NaN,
			aspectRatio: [],
			realPoint: NaN
		};
	},
	methods: {
		async file_load() {
			const pdfPath = this.pdfPath;

			// Setting worker path to worker bundle.
			pdfjsLib.GlobalWorkerOptions.workerSrc =
				"/node_modules/pdfjs-dist/build/pdf.worker.mjs";

			// Loading a document.
			const loadingTask = pdfjsLib.getDocument(pdfPath);
			const pdfDocument = await loadingTask.promise;

			// get number of pages
			this.numberOfPages = pdfDocument.numPages;

			// Request a first page
			const pdfPage = await pdfDocument.getPage(this.page_number);

			// Display page on the existing canvas with 100% scale.
			const viewport = pdfPage.getViewport({ scale: 1.0 });
			const canvas = document.getElementById("theCanvas");
			canvas.width = viewport.width;
			canvas.height = viewport.height;
			const ctx = canvas.getContext("2d");

			// Render PDF content
			const renderTask = pdfPage.render({
				canvasContext: ctx,
				viewport,
			});
			await renderTask.promise;
		},

		addOverlay() {
			this.overlay = true
			//console.log(this.overlay)
		},

		delete_image(index) {
			this.overlays.splice(index, 1);
		},

		handleFileChange(event) {
			// Handle the file change event here
			const selectedFile = event.target.files[0];

			// Check if a file is selected
			if (selectedFile) {
				// Read the file as a data URL
				const reader = new FileReader();

				reader.onload = () => {
					// Create an Image element for downsizing
					const img = new Image();
					img.src = reader.result;

					img.onload = () => {
						// Set the original image data URL
						this.currentImage = reader.result;
						this.aspectRatio = img.width / img.height;

						// Set the new width and height for downscaling
						const newWidth = 250;
						const newHeight = (img.height / img.width) * newWidth;

						// Create a canvas element to draw the downscaled image
						const canvas = document.createElement('canvas');
						const ctx = canvas.getContext('2d');

						canvas.width = newWidth;
						canvas.height = newHeight;

						// Draw the image on the canvas with the new size
						ctx.drawImage(img, 0, 0, newWidth, newHeight);

						// Save the downscaled image as a data URL
						const downscaledImage = canvas.toDataURL();

						// Add the downscaled image data URL to the low_res_img array
						this.low_res_img = downscaledImage;
					};
				};

				reader.readAsDataURL(selectedFile);
			}
		},
		handleMouseMove(event) {
			if (this.isDragging && this.overlay && this.currentImage) {
				// const canvas = event.target;
				// const rect = canvas.getBoundingClientRect();

				// Use canvas coordinates for both starting and ending positions
				const startX = this.dragStartX;
				const startY = this.dragStartY;
				// //console.log(startX, startY, 'dragStartX', 'dragStartY',);
				const endX = event.clientX;
				const endY = event.clientY;

				const minX = Math.min(startX, endX);
				const minY = Math.min(startY, endY);
				const width = Math.abs(endX - startX);
				const height = Math.abs(endY - startY);

				const BgOverlay = this.$refs.BgOverlay;

				BgOverlay.style.position = "absolute";
				BgOverlay.style.left = `${minX}px`;
				BgOverlay.style.top = `${minY}px`;
				BgOverlay.style.width = `${width}px`;
				BgOverlay.style.height = `${height}px`;
				BgOverlay.style.backgroundColor = 'red';
				BgOverlay.style.opacity = "0.1";
				BgOverlay.style.pointerEvents = 'none';

				// Update the position of the red div overlay
				const redOverlay = this.$refs.redOverlay;

				redOverlay.style.position = "absolute";
				redOverlay.style.left = `${minX}px`;
				redOverlay.style.top = `${minY}px`;
				redOverlay.style.width = `${width}px`;
				redOverlay.style.height = `${height}px`;
				redOverlay.style.backgroundImage = 'url(' + this.low_res_img + ')';
				redOverlay.style.backgroundSize = 'contain';
				redOverlay.style.backgroundRepeat = 'no-repeat';
				redOverlay.style.backgroundPosition = 'center';
				redOverlay.style.opacity = "0.3";
				redOverlay.style.pointerEvents = 'none';

				this.left = `${minX}px`;
				this.top = `${minY}px`;
				this.width = `${width}px`;
				this.height = `${height}px`;
				this.img = this.currentImage;
			}
		},
		handleMouseDown(event) {
			//console.log('handleMouseDown');
			// const canvas = event.target;
			// const rect = canvas.getBoundingClientRect();
			if (isNaN(this.currentImage) && this.overlay) {
				//console.log('handleMouseDown - True');
				this.dragStartX = event.clientX;
				this.dragStartY = event.clientY;
				this.isDragging = true;
			}
		},

		fitInnerShape(outer_width, outer_height, inner_aspectRatio) {
			const outer_aspectRatio = outer_width / outer_height;
			if (outer_aspectRatio > inner_aspectRatio) {
				return {
					width: outer_height * inner_aspectRatio,
					height: outer_height
				};
			} else {
				return {
					width: outer_width,
					height: outer_width / inner_aspectRatio
				}
			}
		},

		calculateRealPosition() {
			const realPoint = [];
			let wrong_position = false;

			for (let i = 0; i < this.overlays.length; i++) {
				const overlay = this.overlays[i];
				const width = parseInt(overlay.width, 10);
				const height = parseInt(overlay.height, 10);

				const shape = this.fitInnerShape(width, height, overlay.aspectRatio);

				const midX = parseInt(overlay.left, 10) + width / 2;
				const midY = parseInt(overlay.top, 10) + height / 2;

				const canvas = this.$refs.canvas;
				const rect = canvas.getBoundingClientRect();
				const top = rect.top;
				const left = rect.left;
				const widthCanvas = rect.width;
				const heightCanvas = rect.height;

				let newLeft = midX - shape.width / 2;
				let newTop = midY - shape.height / 2;

				//console.log('unedited top :', newTop, 'edited top', newTop - top);
				//console.log('unedited left :', newLeft, 'edited left', newLeft - left);

				if (newLeft - left < 0) {
					newLeft = 0;
					wrong_position = true
				}

				if (newTop - top < 0) {
					newTop = 0;
					wrong_position = true
				}

				if (newLeft - left + shape.width > widthCanvas) {
					newLeft = widthCanvas - shape.width;
					wrong_position = true;
				}

				if (newTop - top + shape.height > heightCanvas) {
					newTop = heightCanvas - shape.height;
					wrong_position = true;
				}

				realPoint.push({
					'left': newLeft - left,
					'top': newTop - top,
					'width': shape.width,
					'height': shape.height,
					'img': overlay.img,
					'page': overlay.page_number,
				});
			}

			if (wrong_position) {
				console.log('wrong position');
			}

			this.realPoint = realPoint;
			//console.log(this.realPoint);
		},

		handleMouseUp() {
			if (this.overlay && this.currentImage) {
				this.isDragging = false;
				this.overlay = false;
				this.overlays.push({
					"left": this.left,
					"top": this.top,
					"width": this.width,
					"height": this.height,
					img: this.currentImage,
					"low_res_img": this.low_res_img,
					'border_color': 'none',
					'pointerEvents': 'none',
					'page_number': this.page_number,
					'aspectRatio': this.aspectRatio,
					ID: this.overlays.length
				});
				//console.log(this.overlays);
				const redOverlay = this.$refs.redOverlay;
				redOverlay.style.opacity = "0";
				const BgOverlay = this.$refs.BgOverlay;
				BgOverlay.style.opacity = "0";
			}
		},

		handleScaling(index, scale) {
			let div = this.$refs[index][0];
			let styles = window.getComputedStyle(div);
			let right = parseFloat(styles.left) + parseFloat(styles.width); // Right edge position of the div
			console.log('right:', right);
			let bottom = parseFloat(styles.top) + parseFloat(styles.height); // Bottom edge position of the div
			console.log('bottom:', bottom);

			const canvasRect = this.$refs.canvas.getBoundingClientRect();
			const canvasRight = canvasRect.right;
			const canvasBottom = canvasRect.bottom; // Corrected canvas bottom calculation
			console.log('canvasRight:', canvasRight);
			console.log('canvasBottom:', canvasBottom);

			if (right * scale > canvasRight || bottom * scale > canvasBottom || bottom * scale < 0 || right * scale < 0) {
				console.log('Point is outside the canvas');

				// Calculate the difference between scaled canvas size and current div size
				let dx = (canvasRight - right * scale);
				let dy = (canvasBottom - bottom * scale);

				// Adjust div dimensions
				this.overlays[index].width = (parseFloat(styles.width) + dx / scale) + 'px';
				this.overlays[index].height = (parseFloat(styles.height) + dy / scale) + 'px';
				return;
			}

			// Update rectangle dimensions
			this.overlays[index].width = (parseFloat(styles.width) * scale) + 'px';
			this.overlays[index].height = (parseFloat(styles.height) * scale) + 'px';
		},

		handleEdit(index) {
			if (index == this.currentEdit) {
				this.currentEdit = NaN;
				this.overlays.forEach((overlay) => {
					overlay.border_color = 'none';
					overlay.pointerEvents = 'none';

				});
			}
			else {
				this.currentEdit = index;
				// Reset border_color for all overlays
				this.overlays.forEach((overlay, i) => {
					overlay.border_color = i === index ? '2px solid red' : 'none';
					overlay.pointerEvents = i === index ? 'auto' : 'none';
				});
			}
		},
		handleDragStart(index) {
			if (this.currentEdit === index) {
				this.dragging = !this.dragging;
				this.indexDraggedImg = index;
				//console.log(this.indexDraggedImg);
				this.overlays[index].pointerEvents = 'none';
			}
		},
		handleDragging(event) {
			if (this.dragging) {
				// get mouse position
				let mouseX = event.clientX;
				let mouseY = event.clientY;

				// Schedule the update using requestAnimationFrame
				requestAnimationFrame(() => {
					// set new image position
					this.overlays[this.indexDraggedImg].left = `${mouseX + 5}px`;
					this.overlays[this.indexDraggedImg].top = `${mouseY + 5}px`;
				});
			}
		},
		handleDraggingStop() {
			//console.log(this.dragging);
			//console.log(this.indexDraggedImg);
			if (this.dragging && !isNaN(this.indexDraggedImg)) {
				this.dragging = false;
				this.overlays[this.indexDraggedImg].pointerEvents = 'auto';
				this.indexDraggedImg = NaN;
			}
		},

		async handleNext() {
			try {
				this.page_number++;
				await this.file_load();
			} catch (error) {
				//console.log(error);
			}
		},

		async handlePrevious() {
			try {
				if (this.page_number > 1) {
					this.page_number--;
					await this.file_load();
				}
			} catch (error) {
				//console.log(error);
			}

		},

		async fetchRawPdfData(pdfPath) {
			try {
				const response = await fetch(pdfPath);
				if (!response.ok) {
					throw new Error(`Failed to fetch PDF data: ${response.status} - ${response.statusText}`);
				}

				const rawData = await response.blob();
				//console.log(rawData);

				// Convert Blob to data URL
				const dataUrl = await new Promise((resolve) => {
					const reader = new FileReader();
					reader.onloadend = () => resolve(reader.result);
					reader.readAsDataURL(rawData);
				});

				return dataUrl;
			} catch (error) {
				throw new Error(`Error fetching raw PDF data: ${error.message}`);
			}
		},

		async handlePost() {
			const apiUrl = 'http://127.0.0.1:5000/upload';
			const data = await this.exportData();
			try {
				const response = await axios.post(apiUrl, data, {
					headers: {
						'Content-Type': 'application/json'
					},
				});

				console.log(response.data);
			} catch (error) {
				console.error(error);
			}
		},

		async exportData() {
			try {
				// Fetch the raw PDF data
				const rawDataUrl = await this.fetchRawPdfData(this.pdfPath);

				// Calculate real position
				this.calculateRealPosition();

				// Prepare and return the data object
				let data = {
					'Overlays': this.realPoint,
					'PdfFile': rawDataUrl,
				};

				console.log('exportData', data);
				return data;
			} catch (error) {
				console.error('Error fetching raw PDF data:', error);
				// You might want to handle the error or return some default data in case of an error
				return null;
			}
		},
		async handlePageChange() {
			let pageNumber = document.getElementById('pageNumber-input').value;
			try {
				if (pageNumber > 0 && pageNumber <= this.numberOfPages) {
					this.page_number = parseInt(pageNumber);
					await this.file_load();
				}
			} catch (error) {
				//console.log(error);
			}
		}
	},
	mounted() {
		this.file_load();
	},
};
</script>

<style>
body {
	background-color: rgb(66, 66, 66);
}
</style>
